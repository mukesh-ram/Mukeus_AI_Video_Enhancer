import os
import json
import time
import cv2
import threading
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from backend.models.schemas import JobStatusResponse, VideoMetadata
from backend.services.file_manager import (
    create_job_workspace,
    cleanup_job_workspace,
    format_file_size
)
from backend.services.video_info import extract_video_metadata
from backend.services.ffmpeg_service import (
    extract_frames,
    extract_audio,
    reassemble_video
)
from backend.services.realesrgan_service import (
    RealESRGANEnhancer,
    apply_mode_filters,
    resize_to_target_resolution
)
from backend.utils.config import OUTPUT_DIR, HISTORY_FILE
from backend.utils.logger import get_logger

logger = get_logger("processing_service")

# Thread-safe job state tracker
job_store: Dict[str, Dict[str, Any]] = {}
job_lock = threading.Lock()

# Global Real-ESRGAN instance singleton to avoid re-loading PyTorch model weights on every job
_enhancer_instance: Optional[RealESRGANEnhancer] = None
_enhancer_lock = threading.Lock()

def get_enhancer() -> RealESRGANEnhancer:
    global _enhancer_instance
    with _enhancer_lock:
        if _enhancer_instance is None:
            _enhancer_instance = RealESRGANEnhancer(tile_size=256, tile_pad=10)
        return _enhancer_instance

def get_job_status(job_id: str) -> Optional[JobStatusResponse]:
    with job_lock:
        job = job_store.get(job_id)
        if not job:
            return None
        return JobStatusResponse(**job["data"])

def cancel_job(job_id: str) -> bool:
    with job_lock:
        if job_id in job_store:
            job_store[job_id]["cancelled"] = True
            job_store[job_id]["data"]["status"] = "CANCELLED"
            job_store[job_id]["data"]["message"] = "Enhancement cancelled by user."
            logger.info(f"Cancellation requested for job {job_id}")
            return True
        return False

def save_history_record(record: Dict[str, Any]):
    try:
        history_list = []
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    history_list = json.load(f)
            except Exception:
                history_list = []

        history_list.insert(0, record)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history_list, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save history record: {e}")

def update_job(job_id: str, **kwargs):
    with job_lock:
        if job_id in job_store:
            data = job_store[job_id]["data"]
            data.update(kwargs)

def is_cancelled(job_id: str) -> bool:
    with job_lock:
        if job_id in job_store:
            return job_store[job_id].get("cancelled", False)
        return False

def run_enhancement_job(
    job_id: str,
    source_video_path: Path,
    mode: str,
    resolution: str,
    preserve_audio: bool,
    auto_delete_temp: bool
):
    start_time = time.time()
    logger.info(f"Starting processing for job {job_id}: mode={mode}, resolution={resolution}")
    
    subdirs = job_store[job_id]["subdirs"]
    frames_dir = subdirs["frames"]
    enhanced_dir = subdirs["enhanced"]
    audio_path = subdirs["root"] / "audio.aac"
    
    try:
        # STAGE 1: ANALYZING
        update_job(
            job_id,
            status="PROCESSING",
            stage="ANALYZING",
            progress=5.0,
            message="Analyzing video metadata with FFprobe..."
        )
        if is_cancelled(job_id):
            return
            
        orig_metadata = extract_video_metadata(source_video_path)
        update_job(job_id, original_info=orig_metadata)
        
        # STAGE 2: PREPARING & AUDIO EXTRACTION
        update_job(
            job_id,
            stage="PREPARING",
            progress=10.0,
            message="Extracting audio stream..."
        )
        if is_cancelled(job_id):
            return
            
        has_audio = False
        if preserve_audio:
            has_audio = extract_audio(source_video_path, audio_path)

        # STAGE 3: EXTRACTING FRAMES
        update_job(
            job_id,
            stage="EXTRACTING",
            progress=15.0,
            message="Extracting video frames with FFmpeg..."
        )
        if is_cancelled(job_id):
            return
            
        total_frames = extract_frames(source_video_path, frames_dir, image_format="jpg")
        if total_frames == 0:
            raise RuntimeError("No frames extracted from input video clip.")
            
        update_job(job_id, total_frames=total_frames)

        # STAGE 4: AI ENHANCEMENT
        update_job(
            job_id,
            stage="AI_ENHANCEMENT",
            progress=20.0,
            message=f"Initializing Real-ESRGAN AI model ({mode} mode)..."
        )
        
        enhancer = get_enhancer()
        frame_files = sorted(list(frames_dir.glob("frame_*.jpg")))
        
        for idx, frame_path in enumerate(frame_files, start=1):
            if is_cancelled(job_id):
                logger.info(f"Job {job_id} cancelled during frame AI enhancement.")
                cleanup_job_workspace(job_id)
                return

            # Read original frame
            img_bgr = cv2.imread(str(frame_path))
            if img_bgr is None:
                logger.warning(f"Could not read frame {frame_path}, skipping.")
                continue

            # Step A: Real-ESRGAN AI enhancement (Single-pass GPU inference)
            enhanced_bgr = enhancer.enhance_image(img_bgr)
            
            # Step B: Apply Natural / Clean / Strong mode filter (Vectorized GPU filter)
            mode_filtered_bgr = apply_mode_filters(enhanced_bgr, img_bgr, mode)
            
            # Step C: Resize to target resolution
            final_frame_bgr = resize_to_target_resolution(mode_filtered_bgr, resolution, orig_metadata.is_portrait)
            
            # Save enhanced frame in fast JPG format
            out_frame_path = enhanced_dir / frame_path.name
            cv2.imwrite(str(out_frame_path), final_frame_bgr)
            
            # Calculate real progress (between 20% and 85%)
            progress_pct = 20.0 + ((idx / total_frames) * 65.0)
            update_job(
                job_id,
                current_frame=idx,
                progress=round(progress_pct, 1),
                message=f"Enhancing frame {idx} / {total_frames} ({round(progress_pct, 1)}%)"
            )

        # STAGE 5: ENCODING
        update_job(
            job_id,
            stage="ENCODING",
            progress=88.0,
            message="Rebuilding video and encoding H.264 MP4 with FFmpeg..."
        )
        if is_cancelled(job_id):
            return

        output_filename = f"ENHANCED_{orig_metadata.filename}"
        if not output_filename.endswith(".mp4"):
            output_filename = os.path.splitext(output_filename)[0] + ".mp4"
            
        final_output_path = OUTPUT_DIR / output_filename

        reassemble_video(
            frames_dir=enhanced_dir,
            output_video_path=final_output_path,
            fps=orig_metadata.fps,
            audio_path=audio_path if has_audio else None,
            preserve_audio=preserve_audio,
            image_format="jpg"
        )

        # STAGE 6: FINALIZING
        update_job(
            job_id,
            stage="FINALIZING",
            progress=95.0,
            message="Finalizing metadata and cleaning workspace..."
        )

        enhanced_metadata = extract_video_metadata(final_output_path)
        processing_time = round(time.time() - start_time, 2)

        update_job(
            job_id,
            status="COMPLETED",
            stage="COMPLETED",
            progress=100.0,
            message="Enhancement complete!",
            output_filename=output_filename,
            output_path=str(final_output_path),
            enhanced_info=enhanced_metadata,
            processing_time_seconds=processing_time
        )

        # Record history
        save_history_record({
            "job_id": job_id,
            "filename": orig_metadata.filename,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "resolution": f"{enhanced_metadata.width}x{enhanced_metadata.height}",
            "enhancement_mode": mode,
            "processing_time": f"{int(processing_time // 60):02d}:{int(processing_time % 60):02d}",
            "output_location": str(final_output_path),
            "output_filename": output_filename,
            "filesize": enhanced_metadata.filesize_formatted,
            "status": "Completed"
        })

        if auto_delete_temp:
            cleanup_job_workspace(job_id)

    except Exception as e:
        logger.error(f"Error processing job {job_id}: {e}", exc_info=True)
        update_job(
            job_id,
            status="FAILED",
            stage="FAILED",
            progress=0.0,
            message="Enhancement process failed.",
            error=str(e)
        )
        if auto_delete_temp:
            cleanup_job_workspace(job_id)


def start_enhancement(
    source_video_path: Path,
    original_filename: str,
    mode: str,
    resolution: str,
    preserve_audio: bool = True,
    auto_delete_temp: bool = True
) -> str:
    job_id, subdirs = create_job_workspace(original_filename)
    
    initial_status = JobStatusResponse(
        job_id=job_id,
        status="QUEUED",
        stage="ANALYZING",
        progress=0.0,
        current_frame=0,
        total_frames=0,
        message="Job queued for processing...",
        created_at=datetime.now().isoformat()
    )
    
    with job_lock:
        job_store[job_id] = {
            "data": initial_status.dict(),
            "subdirs": subdirs,
            "cancelled": False
        }

    # Launch non-blocking background thread
    t = threading.Thread(
        target=run_enhancement_job,
        args=(job_id, source_video_path, mode, resolution, preserve_audio, auto_delete_temp),
        daemon=True
    )
    t.start()
    
    return job_id
