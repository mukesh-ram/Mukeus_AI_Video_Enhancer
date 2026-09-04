from fastapi import APIRouter, HTTPException
from backend.models.schemas import JobStatusResponse
from backend.services.processing_service import get_job_status, cancel_job
from backend.utils.logger import get_logger

logger = get_logger("api_status")
router = APIRouter(prefix="/api", tags=["Status"])

@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def fetch_status(job_id: str):
    status_resp = get_job_status(job_id)
    if not status_resp:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return status_resp

@router.post("/cancel/{job_id}")
async def cancel_job_endpoint(job_id: str):
    success = cancel_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not active or already finished.")
    return {"job_id": job_id, "status": "CANCELLED", "message": "Enhancement cancelled."}
