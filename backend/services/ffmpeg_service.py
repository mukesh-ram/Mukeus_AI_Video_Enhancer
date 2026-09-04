import os
import subprocess
from pathlib import Path
from typing import Optional
from backend.services.video_info import get_ffmpeg_binary
from backend.utils.logger import get_logger

logger = get_logger("ffmpeg_service")

def extract_frames(video_path: Path, frames_dir: Path, image_format: str = "jpg") -> int:
    ffmpeg_bin = get_ffmpeg_binary()
    output_pattern = str(frames_dir / f"frame_%06d.{image_format}")
    
    cmd = [
        ffmpeg_bin,
        "-y",
        "-i", str(video_path),
        "-q:v", "2",
        "-start_number", "1",
        output_pattern
    ]
    
    logger.info(f"Extracting frames from {video_path} to {frames_dir}...")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        logger.error(f"FFmpeg frame extraction failed: {res.stderr}")
        raise RuntimeError(f"FFmpeg frame extraction error: {res.stderr[:200]}")
        
    extracted_frames = sorted(list(frames_dir.glob(f"frame_*.{image_format}")))
    count = len(extracted_frames)
    logger.info(f"Extracted {count} frames.")
    return count

def extract_audio(video_path: Path, audio_output_path: Path) -> bool:
    ffmpeg_bin = get_ffmpeg_binary()
    
    cmd = [
        ffmpeg_bin,
        "-y",
        "-i", str(video_path),
        "-vn",
        "-acodec", "aac",
        "-b:a", "192k",
        str(audio_output_path)
    ]
    
    logger.info(f"Extracting audio to {audio_output_path}...")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode == 0 and audio_output_path.exists() and audio_output_path.stat().st_size > 0:
        logger.info("Audio extracted successfully.")
        return True
    else:
        logger.warning(f"No audio stream found or audio extraction failed: {res.stderr}")
        return False

def reassemble_video(
    frames_dir: Path,
    output_video_path: Path,
    fps: float,
    audio_path: Optional[Path] = None,
    preserve_audio: bool = True,
    image_format: str = "jpg"
) -> bool:
    ffmpeg_bin = get_ffmpeg_binary()
    input_pattern = str(frames_dir / f"frame_%06d.{image_format}")
    
    cmd = [
        ffmpeg_bin,
        "-y",
        "-framerate", str(fps),
        "-i", input_pattern
    ]
    
    has_audio = preserve_audio and audio_path and audio_path.exists() and audio_path.stat().st_size > 0
    
    if has_audio:
        cmd.extend(["-i", str(audio_path)])
        cmd.extend(["-c:a", "aac", "-b:a", "192k"])
    
    cmd.extend([
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        "-preset", "medium",
        "-shortest",
        str(output_video_path)
    ])
    
    logger.info(f"Reassembling video to {output_video_path} with FPS={fps}, preserve_audio={has_audio}...")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if res.returncode != 0:
        logger.error(f"FFmpeg reassembly failed: {res.stderr}")
        raise RuntimeError(f"FFmpeg video encoding failed: {res.stderr[:300]}")
        
    logger.info(f"Video created successfully at {output_video_path}")
    return True
