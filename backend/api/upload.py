import os
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.models.schemas import VideoMetadata
from backend.services.file_manager import (
    sanitize_filename,
    validate_upload_file
)
from backend.services.video_info import extract_video_metadata
from backend.utils.config import INPUT_DIR
from backend.utils.logger import get_logger

logger = get_logger("api_upload")
router = APIRouter(prefix="/api", tags=["Upload"])

@router.post("/upload", response_model=VideoMetadata)
async def upload_video(file: UploadFile = File(...)):
    filename = sanitize_filename(file.filename or "video.mp4")
    
    # Read first chunk to check size streamingly
    temp_staging_path = INPUT_DIR / filename
    
    total_bytes = 0
    with open(temp_staging_path, "wb") as buffer:
        while True:
            chunk = await file.read(1024 * 1024) # 1MB chunks
            if not chunk:
                break
            total_bytes += len(chunk)
            if total_bytes > 500 * 1024 * 1024:
                buffer.close()
                if temp_staging_path.exists():
                    os.remove(temp_staging_path)
                raise HTTPException(
                    status_code=400,
                    detail="FILE TOO LARGE: Maximum input size is 500 MB."
                )
            buffer.write(chunk)

    valid, err_msg = validate_upload_file(filename, total_bytes)
    if not valid:
        if temp_staging_path.exists():
            os.remove(temp_staging_path)
        raise HTTPException(status_code=400, detail=err_msg)

    try:
        metadata = extract_video_metadata(temp_staging_path)
        return metadata
    except Exception as e:
        logger.error(f"Metadata extraction failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"FFprobe failure reading video metadata: {str(e)}"
        )
