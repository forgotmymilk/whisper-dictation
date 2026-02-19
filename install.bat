@echo off
chcp 65001 >nul
echo ==========================================
echo Whisper Dictation - Portable Setup
echo ==========================================
echo.

:: Get script directory
set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%.venv"

echo Installation directory: %SCRIPT_DIR%

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python first.
    echo Download: https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [OK] Python detected:
python --version
echo.

:: Create virtual environment if not exists
if not exist "%VENV_DIR%" (
    echo [Step 1/5] Creating virtual environment...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: Activate virtual environment
echo.
echo [Step 2/5] Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

:: Upgrade pip
echo.
echo [Step 3/5] Upgrading pip...
python -m pip install --upgrade pip

:: Install faster-whisper
echo.
echo [Step 4/5] Installing faster-whisper...
pip install faster-whisper

:: Install PyTorch with CUDA 12.1
echo.
echo [Step 5/5] Installing PyTorch with CUDA 12.1 (GPU support)...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

:: Install real-time dictation dependencies
echo.
echo [Step 6/6] Installing real-time dictation dependencies...
pip install sounddevice keyboard pyperclip numpy scipy

echo.
echo ==========================================
echo Installation Complete!
echo ==========================================
echo.
echo Virtual environment created at: %VENV_DIR%
echo.
echo Testing GPU availability...
python -c "import torch; print('CUDA Available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
echo.
echo Next steps:
echo 1. Run: start-dictation.bat (for real-time dictation)
echo 2. Run: start-transcribe.bat (for file transcription)
echo.
echo IMPORTANT: First run will download the Large-v3 model (~3GB)
echo.
pause
