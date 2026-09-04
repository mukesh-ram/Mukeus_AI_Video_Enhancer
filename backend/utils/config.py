import os
from pathlib import Path

# Base Directory (Project Root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Application Folders
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
TEMP_DIR = BASE_DIR / "temp"
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models" / "realesrgan"

# Upload Limits
MAX_UPLOAD_SIZE_BYTES = 500 * 1024 * 1024  # 500 MB
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm"}

# History File
HISTORY_FILE = DATA_DIR / "history.json"
SETTINGS_FILE = DATA_DIR / "settings.json"

# AI Model Configuration
MODEL_NAME = "RealESRGAN_x4plus"
MODEL_URL = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"
MODEL_PATH = MODELS_DIR / "RealESRGAN_x4plus.pth"

# GPU Hardware Defaults (GTX 1650 Ti 4GB VRAM)
DEFAULT_TILE_SIZE = 256
DEFAULT_TILE_PAD = 10

# Create required directories automatically
for folder in [INPUT_DIR, OUTPUT_DIR, TEMP_DIR, DATA_DIR, MODELS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)
