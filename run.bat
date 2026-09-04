@echo off
TITLE MUKEUS VIDEO ENHANCER
COLOR 0E

echo ===================================================
echo             MUKEUS VIDEO ENHANCER                  
echo           LOCAL AI VIDEO PROCESSOR                 
echo ===================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ and add it to PATH.
    pause
    exit /b 1
)

:: Create virtual environment if it does not exist
if not exist "venv" (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Install / Upgrade requirements
echo [INFO] Verifying backend dependencies...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo.
echo [INFO] Hardware Check:
python -c "import torch; print('  - PyTorch:', torch.__version__); print('  - CUDA Available:', torch.cuda.is_available()); print('  - Device Name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU Fallback')"
echo.

:: Launch Default Browser
echo [INFO] Launching MUKEUS Web App in default browser...
start http://127.0.0.1:8000

:: Start FastAPI Uvicorn Server
echo [INFO] Starting Local Application Server on http://127.0.0.1:8000 ...
echo [INFO] Press Ctrl+C to stop the application.
echo.
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

pause
