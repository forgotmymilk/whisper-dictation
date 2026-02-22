@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo ==========================================
echo   VoicePro - Portable Launcher
echo ==========================================
echo.

cd /d "%~dp0"

REM Check if the compiled executable exists
set EXE_PATH="dist\VoicePro\VoicePro.exe"

if exist %EXE_PATH% (
    echo [*] Starting VoicePro...
    start "" %EXE_PATH%
    exit /b 0
) else (
    echo [!] VoicePro executable not found at: %EXE_PATH%
    echo [!] Please ensure you have downloaded the fully compiled release,
    echo [!] or run 'build_exe.py' if you are building from source.
    echo.
    pause
    exit /b 1
)
