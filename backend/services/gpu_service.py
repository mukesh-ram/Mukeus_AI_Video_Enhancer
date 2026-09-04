import torch
from backend.models.schemas import GPUInfo
from backend.utils.logger import get_logger

logger = get_logger("gpu_service")

def get_gpu_info() -> GPUInfo:
    cuda_available = torch.cuda.is_available()
    
    if cuda_available:
        try:
            device_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            total_vram = torch.cuda.get_device_properties(0).total_memory / (1024 * 1024)
            
            # Reserved/allocated vs free memory estimation
            allocated_vram = torch.cuda.memory_allocated(0) / (1024 * 1024)
            reserved_vram = torch.cuda.memory_reserved(0) / (1024 * 1024)
            free_vram = total_vram - reserved_vram
            
            status_msg = "CUDA Available - Hardware Acceleration Enabled"
            
            return GPUInfo(
                gpu_name=gpu_name,
                cuda_available=True,
                vram_total_mb=round(total_vram, 1),
                vram_used_mb=round(reserved_vram, 1),
                vram_free_mb=round(free_vram, 1),
                device_count=device_count,
                status_message=status_msg
            )
        except Exception as e:
            logger.error(f"Error querying CUDA details: {e}")
            return GPUInfo(
                gpu_name="NVIDIA GPU (CUDA detected)",
                cuda_available=True,
                vram_total_mb=4096.0,
                vram_used_mb=0.0,
                vram_free_mb=4096.0,
                device_count=1,
                status_message="CUDA Available"
            )
    else:
        return GPUInfo(
            gpu_name="CPU Mode (CUDA Unavailable)",
            cuda_available=False,
            vram_total_mb=0.0,
            vram_used_mb=0.0,
            vram_free_mb=0.0,
            device_count=0,
            status_message="CUDA unavailable. Using CPU mode (slower processing)."
        )
