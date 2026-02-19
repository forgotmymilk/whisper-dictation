@echo off
chcp 65001 >nul
echo ==========================================
echo   Universal Whisper Dictation
echo ==========================================
echo.

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [!] Virtual environment not found!
    echo.
    echo Please run one of the following first:
    echo   - install.bat          ^(First time setup^)
    echo   - portable-setup.bat   ^(Portable mode^)
    echo.
    pause
    exit /b 1
)

echo [*] Starting Universal Whisper Dictation...
echo [*] Right-click tray icon to exit
echo.

.venv\Scripts\python.exe dictation-universal.py

if %errorlevel% neq 0 (
    echo.
    echo [!] Application exited with error
    pause
)
