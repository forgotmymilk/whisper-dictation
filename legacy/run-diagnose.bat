@echo off
chcp 65001 >nul
cd /d "%~dp0"
call .venv\Scripts\activate.bat
echo Running comprehensive diagnostic...
echo.
python diagnose.py
pause
