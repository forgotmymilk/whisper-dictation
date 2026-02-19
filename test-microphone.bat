@echo off
chcp 65001 >nul
echo ==========================================
echo Microphone Diagnostic Tool
echo ==========================================
echo.

cd /d "%~dp0"
call .venv\Scripts\activate.bat

echo Testing audio recording with detailed diagnostics...
echo.

python -c "
import sounddevice as sd
import numpy as np
import tempfile
import os
from scipy.io.wavfile import write as wav_write

print('=== Audio Device Test ===')
print()

# List all input devices
print('Available input devices:')
devices = sd.query_devices()
for i, d in enumerate(devices):
    if d['max_input_channels'] > 0:
        print(f'  [{i}] {d[\"name\"]}')
        print(f'      Channels: {d[\"max_input_channels\"]}, Sample Rate: {d[\"default_samplerate\"]}')
print()

# Get default input device
default_device = sd.query_devices(kind='input')
print(f'Default input device: {default_device[\"name\"]}')
print(f'Device index: {default_device[\"index\"]}')
print()

# Try recording with explicit device
print('Recording 5 seconds of audio...')
print('Please speak clearly into your microphone!')
print()

duration = 5
sample_rate = 16000

try:
    # Record with explicit default device
    recording = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='float32',
        device=default_device['index']
    )
    sd.wait()
    
    # Analyze recording
    max_volume = np.max(np.abs(recording))
    mean_volume = np.mean(np.abs(recording))
    
    print(f'Maximum volume: {max_volume:.4f}')
    print(f'Mean volume: {mean_volume:.4f}')
    print()
    
    if max_volume < 0.01:
        print('❌ Volume too low!')
        print('   Possible causes:')
        print('   1. Microphone muted or volume at 0%')
        print('   2. Wrong microphone selected')
        print('   3. Microphone permissions blocked')
        print()
        print('   Solutions:')
        print('   1. Check Windows Sound Settings')
        print('   2. Increase microphone volume to 70-100%')
        print('   3. Test with another microphone')
    else:
        print('✓ Audio captured successfully!')
        
        # Save test file
        temp_path = os.path.join(tempfile.gettempdir(), 'mic_test.wav')
        wav_write(temp_path, sample_rate, (recording * 32767).astype(np.int16))
        print(f'   Saved test file to: {temp_path}')
        
except Exception as e:
    print(f'❌ Error during recording: {e}')
    print()
    print('Common fixes:')
    print('1. Grant microphone permission to Python in Windows Settings')
    print('2. Set default microphone in Windows Sound Settings')
    print('3. Run this script as Administrator')
"

echo.
echo ==========================================
echo Diagnostic complete.
echo ==========================================
pause
