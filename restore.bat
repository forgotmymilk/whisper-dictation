@echo off
chcp 65001 >nul
echo ==========================================
echo Whisper Dictation - Portable Restore
echo ==========================================
echo.

set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%.venv"

echo This script restores the dictation system on a new Windows installation.
echo.
echo Checking requirements...

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found!
    echo.
    echo Please install Python first:
    echo 1. Visit: https://www.python.org/downloads/
    echo 2. Download Python 3.11 or newer
    echo 3. IMPORTANT: Check "Add Python to PATH" during installation
    echo 4. Reboot and run this script again
    pause
    exit /b 1
)

echo ✅ Python detected
echo.

:: Check for old virtual environment
if exist "%VENV_DIR%" (
    echo Found existing virtual environment.
    choice /C YN /M "Delete and recreate?"
    if errorlevel 2 goto :skip_delete
    rmdir /S /Q "%VENV_DIR%"
    echo Old environment removed.
)

:skip_delete
:: Run full installation
echo.
echo Starting installation...
call "%SCRIPT_DIR%install.bat"
