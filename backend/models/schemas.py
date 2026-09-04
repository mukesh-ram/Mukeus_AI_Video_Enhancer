from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class VideoMetadata(BaseModel):
    filename: str
    filesize_bytes: int
    filesize_formatted: str
    width: int
    height: int
    fps: float
    duration_seconds: float
    duration_formatted: str
    video_codec: str
    audio_codec: str
    bitrate_kbps: Optional[int] = None
    is_portrait: bool = False

class EnhanceRequest(BaseModel):
    job_id: str
    mode: str = Field(default="NATURAL", description="NATURAL, CLEAN, or STRONG")
    resolution: str = Field(default="1080p", description="Original, 720p, or 1080p")
    preserve_audio: bool = True
    auto_delete_temp: bool = True

class JobStatusResponse(BaseModel):
    job_id: str
    status: str  # QUEUED, PROCESSING, COMPLETED, FAILED, CANCELLED
    stage: str   # ANALYZING, PREPARING, EXTRACTING, AI_ENHANCEMENT, ENCODING, FINALIZING, COMPLETED
    progress: float  # 0.0 to 100.0
    current_frame: int = 0
    total_frames: int = 0
    message: str = ""
    output_filename: Optional[str] = None
    output_path: Optional[str] = None
    original_info: Optional[VideoMetadata] = None
    enhanced_info: Optional[VideoMetadata] = None
    error: Optional[str] = None
    created_at: str = ""
    processing_time_seconds: Optional[float] = None

class GPUInfo(BaseModel):
    gpu_name: str
    cuda_available: bool
    vram_total_mb: float
    vram_used_mb: float
    vram_free_mb: float
    device_count: int
    status_message: str

class AppSettings(BaseModel):
    auto_delete_temp: bool = True
    preserve_audio: bool = True
    open_output_folder: bool = True
    output_folder: str = ""
    tile_size: int = 256
