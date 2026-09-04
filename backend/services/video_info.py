import os
import re
import json
import subprocess
from pathlib import Path
from typing import Optional
import imageio_ffmpeg

from backend.models.schemas import VideoMetadata
from backend.services.file_manager import format_file_size
from backend.utils.logger import get_logger

logger = get_logger("video_info")

def get_ffmpeg_binary() -> str:
    try:
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"

def get_ffprobe_binary() -> str:
    ffmpeg_exe = get_ffmpeg_binary()
    dir_name = os.path.dirname(ffmpeg_exe)
    ffprobe_candidate = os.path.join(dir_name, "ffprobe.exe" if os.name == "nt" else "ffprobe")
    if os.path.exists(ffprobe_candidate):
        return ffprobe_candidate
    return "ffprobe"

def format_duration(seconds: float) -> str:
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 100)
    return f"{mins:02d}:{secs:02d}"

def extract_video_metadata(file_path: Path) -> VideoMetadata:
    if not file_path.exists():
        raise FileNotFoundError(f"Video file not found: {file_path}")

    filesize = file_path.stat().st_size
    filename = file_path.name

    ffprobe_bin = get_ffprobe_binary()
    ffmpeg_bin = get_ffmpeg_binary()

    # Strategy 1: Try JSON probe via ffprobe if available
    try:
        cmd = [
            ffprobe_bin,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(file_path)
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        probe_data = json.loads(result.stdout)

        video_stream = None
        audio_stream = None
        for stream in probe_data.get("streams", []):
            if stream.get("codec_type") == "video" and not video_stream:
                video_stream = stream
            elif stream.get("codec_type") == "audio" and not audio_stream:
                audio_stream = stream

        if video_stream:
            width = int(video_stream.get("width", 0))
            height = int(video_stream.get("height", 0))
            v_codec = video_stream.get("codec_name", "h264").upper()
            
            # FPS calculation
            r_fps = video_stream.get("r_frame_rate", "30/1")
            if "/" in r_fps:
                num, den = map(float, r_fps.split("/"))
                fps = num / den if den > 0 else 30.0
            else:
                fps = float(r_fps)

            # Duration
            duration = float(probe_data.get("format", {}).get("duration", 0.0))
            if duration == 0.0 and "duration" in video_stream:
                duration = float(video_stream["duration"])

            # Audio
            a_codec = audio_stream.get("codec_name", "aac").upper() if audio_stream else "None"
            
            # Bitrate
            bitrate_bps = probe_data.get("format", {}).get("bit_rate")
            bitrate_kbps = int(float(bitrate_bps) / 1000) if bitrate_bps else None

            is_portrait = height > width

            return VideoMetadata(
                filename=filename,
                filesize_bytes=filesize,
                filesize_formatted=format_file_size(filesize),
                width=width,
                height=height,
                fps=round(fps, 2),
                duration_seconds=round(duration, 2),
                duration_formatted=format_duration(duration),
                video_codec=v_codec,
                audio_codec=a_codec,
                bitrate_kbps=bitrate_kbps,
                is_portrait=is_portrait
            )
    except Exception as e:
        logger.warning(f"ffprobe direct query failed ({e}). Falling back to ffmpeg -i parser...")

    # Strategy 2: Fallback to parsing `ffmpeg -i` stderr output
    cmd = [ffmpeg_bin, "-i", str(file_path)]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stderr_out = res.stderr

    width, height = 1920, 1080
    fps = 30.0
    duration = 0.0
    v_codec = "H.264"
    a_codec = "AAC"
    bitrate_kbps = None

    # Parse Duration: 00:01:23.45
    dur_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", stderr_out)
    if dur_match:
        h, m, s = dur_match.groups()
        duration = int(h) * 3600 + int(m) * 60 + float(s)

    # Parse Video stream: Video: h264 (...), yuv420p, 1920x1080 [SAR 1:1 DAR 16:9], 60 fps
    res_match = re.search(r"Video:.*?(\d{3,5})x(\d{3,5})", stderr_out)
    if res_match:
        width = int(res_match.group(1))
        height = int(res_match.group(2))

    fps_match = re.search(r"(\d+(?:\.\d+)?)\s*fps", stderr_out)
    if fps_match:
        fps = float(fps_match.group(1))

    codec_match = re.search(r"Video:\s*(\w+)", stderr_out)
    if codec_match:
        v_codec = codec_match.group(1).upper()

    audio_match = re.search(r"Audio:\s*(\w+)", stderr_out)
    if audio_match:
        a_codec = audio_match.group(1).upper()
    else:
        a_codec = "None"

    bitrate_match = re.search(r"bitrate:\s*(\d+)\s*kb/s", stderr_out)
    if bitrate_match:
        bitrate_kbps = int(bitrate_match.group(1))

    is_portrait = height > width

    return VideoMetadata(
        filename=filename,
        filesize_bytes=filesize,
        filesize_formatted=format_file_size(filesize),
        width=width,
        height=height,
        fps=round(fps, 2),
        duration_seconds=round(duration, 2),
        duration_formatted=format_duration(duration),
        video_codec=v_codec,
        audio_codec=a_codec,
        bitrate_kbps=bitrate_kbps,
        is_portrait=is_portrait
    )
