# MUKEUS VIDEO ENHANCER 🎮✨

A creator-focused AI video enhancement application built for YouTube gaming content, gaming streams, and clips (Shorts / 16:9 / 9:16).

Run it **locally** on your PC or **virtually for FREE** on Google Colab's NVIDIA T4 GPU (with 0 load on your PC).

---

## ⚡ Option 1: Run Virtually on Google Colab (0 Load on your PC - 100% Free GPU)

1. Open [Google Colab](https://colab.research.google.com/).
2. Upload **[`MUKEUS_VIDEO_ENHANCER_COLAB.ipynb`](file:///d:/Projects/Mukeus_AI_Enhancer/MUKEUS_VIDEO_ENHANCER_COLAB.ipynb)**.
3. Select **Runtime ➔ Change runtime type ➔ T4 GPU**.
4. Run Cell 1 & Cell 2.
5. Click the generated public link to open the MUKEUS UI!

---

## 💻 Option 2: Run Locally on Windows (GTX 1650 Ti GPU)

1. Open your project folder: `d:\Projects\Mukeus_AI_Enhancer`
2. Double-click **`run.bat`**.
3. It will launch the application and open **`http://127.0.0.1:8000`** in your default browser.

---

## Key Features

- **Natural Gaming Real-ESRGAN Model**: Custom FP16 PyTorch inference pipeline tuned for gaming footage (keeps textures natural without oversharpening or artificial halos).
- **3 Enhancement Modes**:
  - **NATURAL (Recommended)**: Balanced enhancement preserving original game details.
  - **CLEAN**: Moderate denoise filter + AI enhancement for compressed stream clips.
  - **STRONG**: Stronger reconstruction for heavily pixelated clips.
- **Aspect Ratio & Shorts Preservation**: Auto-detects 16:9 landscape (1920x1080) and 9:16 vertical YouTube Shorts (1080x1920) without stretching or cropping.
- **VRAM & Hardware Optimization**: Tiled processing engine prevents Out-Of-Memory (OOM) crashes.
- **Original Audio Muxing**: Preserves game audio commentary, microphone streams, and sound effects using FFmpeg.
- **Real-Time Frame Progress**: Shows exact frame count (e.g. `Frame 1842 / 2350`) and step progress.
- **Side-by-Side Dual Video Preview**: Instant browser video playback comparing Original vs Enhanced clips.

---

## Project Structure

```
d:/Projects/Mukeus_AI_Enhancer/
├── MUKEUS_VIDEO_ENHANCER_COLAB.ipynb  # Free Colab Virtual GPU Notebook
├── backend/
│   ├── main.py               # FastAPI entry point
│   ├── api/                  # REST API routes (upload, enhance, status, download, history, settings)
│   ├── services/             # Core logic (video_info, ffmpeg_service, realesrgan_service, processing_service, gpu_service)
│   ├── models/               # Pydantic schemas
│   └── utils/                # Config & logger
├── frontend/
│   ├── index.html            # MUKEUS UI
│   ├── css/                  # Dark gaming design system
│   └── js/                   # Vanilla JavaScript modules
├── models/realesrgan/        # Auto-downloaded model weights
├── input/                    # Staged video clips
├── output/                   # Enhanced MP4 output files
├── temp/                     # Per-job temp frame workspace
├── data/                     # Local history.json storage
├── requirements.txt
├── run.bat
└── README.md
```
