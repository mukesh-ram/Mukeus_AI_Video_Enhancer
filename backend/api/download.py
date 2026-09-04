from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from backend.services.processing_service import get_job_status
from backend.utils.config import OUTPUT_DIR, INPUT_DIR
from backend.utils.logger import get_logger

logger = get_logger("api_download")
router = APIRouter(prefix="/api", tags=["Download & Streaming"])

@router.get("/download/{job_id}")
async def download_enhanced(job_id: str):
    job = get_job_status(job_id)
    if not job or not job.output_filename:
        # Check if job_id is direct filename
        target_path = OUTPUT_DIR / job_id
        if target_path.exists():
            return FileResponse(
                path=target_path,
                filename=target_path.name,
                media_type="video/mp4"
            )
        raise HTTPException(status_code=404, detail="Enhanced video output not found.")

    target_path = OUTPUT_DIR / job.output_filename
    if not target_path.exists():
        raise HTTPException(status_code=404, detail=f"File {job.output_filename} not found on disk.")

    return FileResponse(
        path=target_path,
        filename=job.output_filename,
        media_type="video/mp4"
    )

@router.get("/video-file/input/{filename}")
async def stream_input_video(filename: str):
    target = INPUT_DIR / filename
    if not target.exists():
        raise HTTPException(status_code=404, detail="Input file not found.")
    return FileResponse(path=target, media_type="video/mp4")

@router.get("/video-file/output/{filename}")
async def stream_output_video(filename: str):
    target = OUTPUT_DIR / filename
    if not target.exists():
        raise HTTPException(status_code=404, detail="Output file not found.")
    return FileResponse(path=target, media_type="video/mp4")
