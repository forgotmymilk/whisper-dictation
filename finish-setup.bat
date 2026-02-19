@echo off
chcp 65001 >nul
echo ==========================================
echo Complete Whisper Setup with Python 3.11
echo ==========================================
echo.

cd /d "%~dp0"

echo [Step 1/5] Checking Python version...
python --version
echo.

:: Remove old virtual environment
echo [Step 2/5] Removing old virtual environment...
if exist ".venv" (
    rmdir /S /Q .venv
    echo [OK] Old environment removed
) else (
    echo [OK] No old environment found
)

:: Create new virtual environment
echo.
echo [Step 3/5] Creating new virtual environment with Python 3.11...
python -m venv .venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    echo Make sure Python 3.11 is in your PATH
    pause
    exit /b 1
)
echo [OK] Virtual environment created

:: Activate and install
echo.
echo [Step 4/5] Installing PyTorch with CUDA 12.1 (GPU support)...
echo This downloads ~2GB and takes 10-15 minutes
echo Please wait and DO NOT close this window...
echo.

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip

:: Install PyTorch with GPU support
echo Installing PyTorch (GPU version for RTX 4070 Ti Super)...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --no-cache-dir

if errorlevel 1 (
    echo.
    echo [WARNING] GPU installation failed. Trying CPU fallback...
    pip install torch torchvision torchaudio
    echo [INFO] CPU version installed. GPU acceleration not available.
    echo [TIP] You may need to install CUDA toolkit from NVIDIA
) else (
    echo [OK] PyTorch with GPU support installed
)

:: Install other dependencies
echo.
echo [Step 5/5] Installing dictation dependencies...
pip install faster-whisper sounddevice keyboard pyperclip numpy scipy

:: Final test
echo.
echo ==========================================
echo Testing Installation
echo ==========================================
python -c "
import torch
print('PyTorch version:', torch.__version__)
print('CUDA available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('GPU:', torch.cuda.get_device_name(0))
    print('VRAM:', torch.cuda.get_device_properties(0).total_memory / 1024**3, 'GB')
else:
    print('WARNING: GPU not detected - using CPU mode')
"

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Run: test-setup.bat     (verify everything works)
echo 2. Run: start-dictation.bat (start dictating!)
echo.
pause
