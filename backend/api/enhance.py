from fastapi import APIRouter, HTTPException
from backend.models.schemas import EnhanceRequest
from backend.services.processing_service import start_enhancement
from backend.utils.config import INPUT_DIR
from backend.utils.logger import get_logger

logger = get_logger("api_enhance")
router = APIRouter(prefix="/api", tags=["Enhance"])

@router.post("/enhance")
async def trigger_enhancement(req: EnhanceRequest):
    # Locate staged file in INPUT_DIR matching job_id or filename
    filename = req.job_id
    video_path = INPUT_DIR / filename
    
    if not video_path.exists():
        # Try finding file in INPUT_DIR
        input_files = list(INPUT_DIR.glob("*"))
        matching_file = None
        for f in input_files:
            if f.name == filename or req.job_id in f.name:
                matching_file = f
                break
        if matching_file:
            video_path = matching_file
        else:
            raise HTTPException(status_code=404, detail=f"Source video file '{filename}' not found in staging input.")

    job_id = start_enhancement(
        source_video_path=video_path,
        original_filename=video_path.name,
        mode=req.mode,
        resolution=req.resolution,
        preserve_audio=req.preserve_audio,
        auto_delete_temp=req.auto_delete_temp
    )

    return {"job_id": job_id, "status": "QUEUED", "message": "Enhancement job initiated."}
