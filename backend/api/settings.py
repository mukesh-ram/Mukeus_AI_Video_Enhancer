import os
import json
import subprocess
from fastapi import APIRouter, HTTPException
from backend.models.schemas import AppSettings, GPUInfo
from backend.services.gpu_service import get_gpu_info
from backend.utils.config import SETTINGS_FILE, OUTPUT_DIR
from backend.utils.logger import get_logger

logger = get_logger("api_settings")
router = APIRouter(prefix="/api", tags=["Settings"])

def load_settings() -> AppSettings:
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return AppSettings(**data)
        except Exception:
            pass
    s = AppSettings(output_folder=str(OUTPUT_DIR))
    save_settings(s)
    return s

def save_settings(s: AppSettings):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(s.dict(), f, indent=2)
    except Exception as e:
        logger.error(f"Error saving settings: {e}")

@router.get("/gpu", response_model=GPUInfo)
async def fetch_gpu_info():
    return get_gpu_info()

@router.get("/settings", response_model=AppSettings)
async def fetch_settings():
    return load_settings()

@router.post("/settings", response_model=AppSettings)
async def update_settings(settings: AppSettings):
    save_settings(settings)
    return settings

@router.post("/open-output-folder")
async def open_output_folder():
    try:
        folder = str(OUTPUT_DIR.resolve())
        if os.name == "nt":
            os.startfile(folder)
        else:
            subprocess.run(["open" if os.uname().sysname == "Darwin" else "xdg-open", folder])
        return {"message": f"Opened output folder: {folder}"}
    except Exception as e:
        logger.error(f"Failed to open output folder: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to open explorer: {str(e)}")
