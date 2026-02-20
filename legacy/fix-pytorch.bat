@echo off
chcp 65001 >nul
echo ==========================================
echo Fix: Install PyTorch with CUDA
echo ==========================================
echo.

cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo Virtual environment not found!
    echo Run install.bat first.
    pause
    exit /b 1
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Installing PyTorch with CUDA 12.1...
echo This may take 5-10 minutes...
echo.

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --force-reinstall

echo.
echo Testing installation...
python -c "import torch; print('PyTorch installed:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"

echo.
echo Done! Run test-setup.bat to verify.
pause
