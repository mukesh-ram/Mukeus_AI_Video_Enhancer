import os
import re
import shutil
import uuid
from pathlib import Path
from typing import Tuple, Dict
from backend.utils.config import TEMP_DIR, INPUT_DIR, OUTPUT_DIR, ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE_BYTES
from backend.utils.logger import get_logger

logger = get_logger("file_manager")

def sanitize_filename(filename: str) -> str:
    # Remove path traversal characters and unsafe symbols
    clean = os.path.basename(filename)
    clean = re.sub(r'[^\w\s\.-]', '_', clean)
    clean = clean.strip()
    return clean if clean else "clip.mp4"

def format_file_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def create_job_workspace(original_filename: str) -> Tuple[str, Dict[str, Path]]:
    job_id = str(uuid.uuid4())[:8]
    job_dir = TEMP_DIR / job_id
    
    subdirs = {
        "root": job_dir,
        "source": job_dir / "source",
        "frames": job_dir / "frames",
        "enhanced": job_dir / "enhanced",
        "logs": job_dir / "logs"
    }
    
    for folder in subdirs.values():
        folder.mkdir(parents=True, exist_ok=True)
        
    logger.info(f"Created job workspace for job {job_id} at {job_dir}")
    return job_id, subdirs

def cleanup_job_workspace(job_id: str) -> bool:
    job_dir = TEMP_DIR / job_id
    if job_dir.exists():
        try:
            shutil.rmtree(job_dir, ignore_errors=True)
            logger.info(f"Cleaned up job workspace: {job_dir}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete job workspace {job_dir}: {e}")
            return False
    return True

def validate_upload_file(filename: str, file_size: int) -> Tuple[bool, str]:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file format '{ext}'. Allowed: MP4, MOV, MKV, WEBM."
    
    if file_size > MAX_UPLOAD_SIZE_BYTES:
        return False, f"FILE TOO LARGE: Size ({format_file_size(file_size)}) exceeds maximum allowed size of 500 MB."
    
    return True, "Valid"
