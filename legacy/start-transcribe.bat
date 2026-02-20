@echo off
chcp 65001 >nul
cd /d "%~dp0"

:: Check if venv exists
if not exist ".venv\Scripts\activate.bat" (
    echo Virtual environment not found!
    echo Please run install.bat first.
    pause
    exit /b 1
)

:: Get audio file argument
set "AUDIO_FILE=%~1"

:: Activate and run
call .venv\Scripts\activate.bat

if "%~1"=="" (
    python transcribe.py
) else (
    python transcribe.py "%~1"
)

pause
