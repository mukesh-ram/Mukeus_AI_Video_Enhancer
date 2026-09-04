import json
from fastapi import APIRouter, HTTPException
from backend.utils.config import HISTORY_FILE
from backend.utils.logger import get_logger

logger = get_logger("api_history")
router = APIRouter(prefix="/api", tags=["History"])

@router.get("/history")
async def get_history():
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading history.json: {e}")
        return []

@router.delete("/history")
async def clear_history():
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return {"message": "History cleared successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
