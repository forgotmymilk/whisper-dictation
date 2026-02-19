@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo ==========================================
echo   Portable Setup Wizard
echo   便携版安装向导
echo ==========================================
echo.

cd /d "%~dp0"

REM Check if already set up
if exist ".venv\Scripts\python.exe" (
    echo [?] Virtual environment already exists.
    choice /C YN /M "Reinstall? "
    if !errorlevel! equ 2 (
        echo.
        echo Setup cancelled.
        pause
        exit /b 0
    )
    echo [*] Removing old environment...
    rmdir /s /q .venv
)

echo.
echo [*] Creating virtual environment...
python -m venv .venv
if !errorlevel! neq 0 (
    echo [!] Failed to create virtual environment
    echo [!] Please ensure Python 3.8+ is installed
    pause
    exit /b 1
)

echo [*] Activating environment...
call .venv\Scripts\activate.bat

echo [*] Upgrading pip...
python -m pip install --upgrade pip -q

echo.
echo [*] Installing dependencies...
echo   - PyTorch (with CUDA support if available)...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 -q 2>nul
if !errorlevel! neq 0 (
    echo   - CUDA not available, installing CPU version...
    pip install torch torchvision torchaudio -q
)

echo   - Faster Whisper...
pip install faster-whisper -q

echo   - Audio and input libraries...
pip install sounddevice numpy scipy keyboard pyperclip -q

echo.
echo [*] Installation complete!
echo.

REM Create initial config
echo [*] Creating configuration files...
if not exist "user-config.json" (
    echo {> user-config.json
    echo   "hotkey": "f15",>> user-config.json
    echo   "language": null,>> user-config.json
    echo   "model": "auto",>> user-config.json
    echo   "compute_type": "auto",>> user-config.json
    echo   "device": "auto",>> user-config.json
    echo   "enable_punctuation": true,>> user-config.json
    echo   "enable_formatting": true,>> user-config.json
    echo   "enable_capitalization": true,>> user-config.json
    echo   "output_mode": "type">> user-config.json
    echo }>> user-config.json
)

echo.
echo ==========================================
echo   Setup Complete! 
echo ==========================================
echo.
echo Next steps:
echo   1. Run 'start-universal.bat' to start
echo   2. Follow the setup wizard on first run
echo   3. Configure your hotkey in the wizard
echo.
echo Tips:
echo   - Use F15-F20 for mouse button mapping
echo   - Run setup again anytime by deleting:
echo     user-config.json and device-profile.json
echo.
pause
