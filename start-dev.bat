@echo off
chcp 65001 >nul

:: ---- Auto-elevate to Administrator ----
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Requesting Administrator privileges...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b 0
)

echo ==========================================
echo   VoicePro - Development Mode
echo ==========================================
echo.

cd /d "%~dp0"

:: Check for virtual environment
if not exist ".venv\Scripts\python.exe" (
    echo [!] Virtual environment not found!
    echo     Please run: python -m venv .venv
    echo     Then:       .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

echo [*] Starting VoicePro from source code...
echo [*] Running as Administrator
echo [*] Hold F15 to dictate, right-click tray icon to exit
echo.

.venv\Scripts\python.exe dictation-universal.py

if %errorlevel% neq 0 (
    echo.
    echo [!] Application exited with error
    pause
)
