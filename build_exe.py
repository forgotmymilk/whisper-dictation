import os
import subprocess
import sys
import shutil

def clean_build_dirs():
    """Remove old build directories to ensure a clean build."""
    for d in ["build", "dist"]:
        if os.path.exists(d):
            print(f"Cleaning {d} directory...")
            try:
                shutil.rmtree(d)
            except Exception as e:
                print(f"Warning: Could not remove {d} directory: {e}")

def build_executable():
    """Run PyInstaller with the correct arguments to build the executable."""
    print("Building Universal Whisper Dictation executable...")
    
    # Path to the main script
    main_script = "dictation-universal.py"
    
    # We must explicitly include faster_whisper models if any are bundled, 
    # but initially models are downloaded at runtime to save space. 
    # However, Python dependencies like CTranslate2 need specific handling.
    
    # Construct the PyInstaller command
    # -F: Create a single-file executable (or -D for a 1-folder distribution, -D is usually safer for CTranslate2)
    # -w: Windowed mode (no console window by default, since we handle our own console minimization) 
    #     WAIT: Since it's a CLI tool at heart with a tray icon, we should probably keep the console 
    #     but let our auto-minimize logic handle it, so DON'T use -w. Use -c (console).
    # --icon: Add an app icon if we have one (skip for now)
    
    # NOTE: CTranslate2 and faster-whisper are notorious for PyInstaller issues.
    # We will use a one-folder distribution (-D) first as it is much more reliable with large AI libs.
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "VoicePro",
        "--console", 
        "--onedir", # Use one-folder instead of one-file initially for stability with AI libraries
        "--clean",
        "--hidden-import", "faster_whisper",
        "--hidden-import", "ctranslate2",
        "--hidden-import", "pystray",
        "--hidden-import", "PIL",
        "--hidden-import", "customtkinter",
        "--add-data", "settings_gui.py;.", # Include settings_gui.py so it can be launched via subprocess
        "--add-data", "ai_presets.py;.",
        main_script
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    
    print("\n✅ Build complete! Executable is located in the 'dist/VoicePro' directory.")
    print("   Note: The 'dist/VoicePro' directory contains all dependencies.")
    print("   Zip this directory to distribute the portable application.")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    
    clean_build_dirs()
    build_executable()
