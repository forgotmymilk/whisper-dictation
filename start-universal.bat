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
echo   VoicePro - Universal Whisper Dictation
echo ==========================================
echo.

cd /d "%~dp0"

:: ---- Strategy: Prefer source mode if .venv exists ----
:: This ensures developers always run the latest code.
:: For portable deployment (no .venv), it falls back to the bundled exe.

if exist ".venv\Scripts\python.exe" (
    echo [*] Virtual environment found - running from source code
    echo [*] Running as Administrator
    echo.
    .venv\Scripts\python.exe dictation-universal.py
    goto :end
)

:: ---- Fallback: Run from bundled executable ----
set EXE_PATH=dist\VoicePro\VoicePro.exe

if not exist "%EXE_PATH%" (
    echo [!] Neither .venv nor bundled executable found!
    echo.
    echo For developers: run 'python -m venv .venv' then 'pip install -r requirements.txt'
    echo For users:      download the pre-built release from GitHub
    echo.
    pause
    exit /b 1
)

echo [*] Starting VoicePro from bundled executable...
echo [*] Running as Administrator
echo.

start "" "%EXE_PATH%"

:end
if %errorlevel% neq 0 (
    echo.
    echo [!] Application exited with error code: %errorlevel%
    pause
)
