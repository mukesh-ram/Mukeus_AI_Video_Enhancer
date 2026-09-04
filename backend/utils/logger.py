import logging
import sys
from backend.utils.config import DATA_DIR

log_file = DATA_DIR / "app.log"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, encoding="utf-8")
    ]
)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
