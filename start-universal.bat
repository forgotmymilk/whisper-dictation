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
echo   Universal Whisper Dictation
echo ==========================================
echo.

cd /d "%~dp0"

set EXE_PATH="dist\VoicePro\VoicePro.exe"

if not exist %EXE_PATH% (
    echo [!] VoicePro executable not found!
    echo.
    echo Please ensure you have downloaded the fully compiled release,
    echo or run 'build_exe.py' if you are building from source.
    echo.
    pause
    exit /b 1
)

echo [*] Starting VoicePro...
echo [*] Running as Administrator
echo [*] Right-click tray icon to exit
echo.

start "" %EXE_PATH%

if %errorlevel% neq 0 (
    echo.
    echo [!] Application exited with error
    pause
)
