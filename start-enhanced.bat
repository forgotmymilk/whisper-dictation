@echo off
chcp 65001 >nul
echo ==========================================
echo   Enhanced Whisper Dictation
echo   智能语音输入系统
echo ==========================================
echo.

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found!
    echo Please run install.bat first.
    pause
    exit /b 1
)

.venv\Scripts\python.exe dictation-enhanced.py

pause
