import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.api import upload, enhance, status, download, history, settings
from backend.utils.config import BASE_DIR, OUTPUT_DIR, INPUT_DIR
from backend.utils.logger import get_logger

logger = get_logger("main")

app = FastAPI(
    title="MUKEUS VIDEO ENHANCER API",
    description="Local AI Video Enhancement Server for YouTube Gaming Content",
    version="1.0.0"
)

# Enable CORS for local origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(upload.router)
app.include_router(enhance.router)
app.include_router(status.router)
app.include_router(download.router)
app.include_router(history.router)
app.include_router(settings.router)

# Mount Frontend static files
frontend_path = BASE_DIR / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

@app.get("/")
async def serve_index():
    index_file = BASE_DIR / "frontend" / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "MUKEUS VIDEO ENHANCER Backend Running. Frontend index.html not found."}

@app.on_event("startup")
async def startup_event():
    logger.info("==========================================")
    logger.info("   MUKEUS VIDEO ENHANCER - LOCAL SERVER   ")
    logger.info("==========================================")
    logger.info(f"Root path: {BASE_DIR}")
    logger.info(f"Input path: {INPUT_DIR}")
    logger.info(f"Output path: {OUTPUT_DIR}")
