#!/usr/bin/env python3
"""
Quick test to verify Faster-Whisper installation
"""

import sys

def test_imports():
    print("Testing imports...")
    errors = []
    
    try:
        import torch
        print(f"✓ PyTorch {torch.__version__}")
        if torch.cuda.is_available():
            print(f"  └─ GPU: {torch.cuda.get_device_name(0)}")
        else:
            print("  └─ ⚠️ CUDA not available (will use CPU)")
    except ImportError:
        errors.append("PyTorch not installed")
        print("❌ PyTorch not installed")
    
    try:
        from faster_whisper import WhisperModel
        print("✓ Faster-Whisper")
    except ImportError:
        errors.append("faster-whisper not installed")
        print("❌ faster-whisper not installed")
    
    try:
        import sounddevice as sd
        print("✓ SoundDevice (audio capture)")
    except ImportError:
        errors.append("sounddevice not installed")
        print("❌ sounddevice not installed")
    
    try:
        import keyboard
        print("✓ Keyboard (hotkeys)")
    except ImportError:
        errors.append("keyboard not installed")
        print("❌ keyboard not installed")
    
    try:
        import pyperclip
        print("✓ Pyperclip (clipboard)")
    except ImportError:
        errors.append("pyperclip not installed")
        print("❌ pyperclip not installed")
    
    return len(errors) == 0

def test_microphone():
    print("\nTesting microphone...")
    try:
        import sounddevice as sd
        import numpy as np
        
        # List devices
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        
        if input_devices:
            print(f"✓ Found {len(input_devices)} input device(s):")
            for d in input_devices:
                print(f"  - {d['name']}")
            return True
        else:
            print("⚠️ No microphone detected")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Faster-Whisper Installation Test")
    print("=" * 50)
    
    imports_ok = test_imports()
    mic_ok = test_microphone()
    
    print("\n" + "=" * 50)
    if imports_ok and mic_ok:
        print("✅ All tests passed! Ready to use dictation.")
        print("\nNext steps:")
        print("  1. start-dictation.bat    (real-time dictation)")
        print("  2. start-transcribe.bat   (file transcription)")
    else:
        print("❌ Some tests failed. Run install.bat to fix.")
        if not imports_ok:
            print("\nMissing packages detected. Run:")
            print("  install.bat")
    print("=" * 50)
    
    input("\nPress Enter to exit...")
