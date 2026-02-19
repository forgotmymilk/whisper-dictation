@echo off
chcp 65001 >nul
echo ==========================================
echo Fix: Microphone Access for Whisper Dictation
echo ==========================================
echo.
echo 🔴 PROBLEM: No audio captured when holding hotkey
echo.
echo Common causes:
echo 1. Windows blocking microphone access
echo 2. Wrong microphone selected
echo 3. Microphone muted or volume too low
echo.
echo ==========================================
echo SOLUTION 1: Check Windows Privacy Settings
echo ==========================================
echo.
echo Step 1: Opening Windows Privacy Settings...
echo (Please check the settings window that opens)
start ms-settings:privacy-microphone
echo.
echo 👉 IN THE SETTINGS WINDOW:
echo    1. Turn ON "Microphone access"
echo    2. Turn ON "Let apps access your microphone"
echo    3. Scroll down to "Allow desktop apps"
echo    4. Make sure Terminal/Command Prompt is allowed
echo.
pause

echo.
echo ==========================================
echo SOLUTION 2: Set Default Microphone
echo ==========================================
echo.
echo Opening Sound Settings...
start ms-settings:sound
echo.
echo 👉 IN SOUND SETTINGS:
echo    1. Under "Input" select your microphone
echo    2. Click "Device properties"
echo    3. Set volume to 80-100%%
echo    4. Test the microphone
echo.
pause

echo.
echo ==========================================
echo SOLUTION 3: Test with Check Script
echo ==========================================
echo.
echo Running microphone test...
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python check-mic.py

echo.
echo ==========================================
echo SOLUTION 4: Run as Administrator
echo ==========================================
echo.
echo If none of the above work, try:
echo.
echo 1. Right-click on start-dictation.bat
echo 2. Select "Run as administrator"
echo 3. Try dictating again
echo.
echo Administrator mode bypasses some permission issues.
echo.
pause
