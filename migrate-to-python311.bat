@echo off
chcp 65001 >nul
echo ==========================================
echo Python 3.11 Migration for Whisper Dictation
echo ==========================================
echo.

:: Check current Python version
echo [Step 1/6] Checking current Python version...
for /f "tokens=*" %%a in ('python --version 2^>^&1') do set CURRENT_PY=%%a
echo Current: %CURRENT_PY%

echo.
echo [WARNING] This will replace your Python with 3.11
echo Your RTX 4070 Ti Super needs Python 3.11 for GPU acceleration
echo.
choice /C YN /M "Continue?"
if errorlevel 2 exit /b 1

:: Download Python 3.11 from Aliyun mirror (China-friendly)
echo.
echo [Step 2/6] Downloading Python 3.11 from Aliyun mirror...
echo This may take 2-3 minutes...
set "PYTHON_INSTALLER=%TEMP%\python-3.11.9-amd64.exe"
powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://mirrors.aliyun.com/python-release/Windows/python-3.11.9-amd64.exe' -OutFile '%PYTHON_INSTALLER%' -UseBasicParsing"

if not exist "%PYTHON_INSTALLER%" (
    echo [ERROR] Download failed. Trying alternative mirror...
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://mirrors.tuna.tsinghua.edu.cn/python-release/Windows/python-3.11.9-amd64.exe' -OutFile '%PYTHON_INSTALLER%' -UseBasicParsing"
)

if not exist "%PYTHON_INSTALLER%" (
    echo [ERROR] Download failed from all mirrors.
    echo Please download manually from: https://www.python.org/downloads/release/python-3119/
    pause
    exit /b 1
)

echo [OK] Downloaded to %PYTHON_INSTALLER%

:: Install Python 3.11
echo.
echo [Step 3/6] Installing Python 3.11...
echo IMPORTANT: Check "Add Python to PATH" in the installer!
echo.
echo Click OK to start installer...
pause

"%PYTHON_INSTALLER%" /passive InstallAllUsers=1 PrependPath=1 Include_test=0

echo.
echo [INFO] Installation started. Waiting for completion...
timeout /t 10 /nobreak >nul

:: Verify Python 3.11
echo.
echo [Step 4/6] Verifying Python 3.11 installation...
python --version 2>nul | findstr "3.11" >nul
if errorlevel 1 (
    echo [WARNING] Python 3.11 not detected in PATH
    echo Please restart this batch file as Administrator
    pause
    exit /b 1
)

echo [OK] Python 3.11 installed: 
python --version

:: Remove old virtual environment
echo.
echo [Step 5/6] Recreating virtual environment with Python 3.11...
cd /d "%~dp0"

if exist ".venv" (
    echo Removing old virtual environment...
    rmdir /S /Q .venv
)

python -m venv .venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

echo [OK] Virtual environment created

:: Install PyTorch with GPU support
echo.
echo [Step 6/6] Installing PyTorch with CUDA 12.1 (GPU support)...
echo This will take 10-15 minutes. Please wait...
echo.

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip

:: Install PyTorch with CUDA
echo Installing PyTorch (GPU version)...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

if errorlevel 1 (
    echo.
    echo [WARNING] GPU installation failed. Trying CPU version...
    pip install torch torchvision torchaudio
    echo [INFO] Installed CPU version. GPU acceleration not available.
)

:: Install other dependencies
echo.
echo Installing remaining dependencies...
pip install faster-whisper sounddevice keyboard pyperclip numpy scipy

:: Test installation
echo.
echo Testing installation...
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"

echo.
echo ==========================================
echo Migration Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Run: start-dictation.bat (for real-time dictation)
echo 2. Run: start-transcribe.bat (for file transcription)
echo.

:: Cleanup
del "%PYTHON_INSTALLER%" 2>nul

pause
