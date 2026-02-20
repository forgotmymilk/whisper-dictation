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

:: Activate and run
call .venv\Scripts\activate.bat
python dictation.py
pause
