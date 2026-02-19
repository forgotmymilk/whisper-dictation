#!/usr/bin/env python3
"""
Microphone permission and configuration fix for Windows
"""

import sounddevice as sd
import numpy as np

print("=" * 60)
print("🎤 Microphone Configuration Test")
print("=" * 60)
print()

# Show current default input
print("Current default input device:")
try:
    default = sd.query_devices(kind='input')
    print(f"  Name: {default['name']}")
    print(f"  Index: {default['index']}")
    print(f"  Channels: {default['max_input_channels']}")
    print(f"  Sample Rate: {default['default_samplerate']}")
except Exception as e:
    print(f"  Error: {e}")

print()
print("Testing recording with default device...")
print("Please speak for 3 seconds...")

try:
    # Record for 3 seconds
    duration = 3
    fs = 16000
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    
    # Check if we got audio
    max_val = np.max(np.abs(recording))
    mean_val = np.mean(np.abs(recording))
    
    print(f"\nMax amplitude: {max_val:.4f}")
    print(f"Mean amplitude: {mean_val:.4f}")
    
    if max_val < 0.01:
        print("\n❌ PROBLEM: No audio captured!")
        print("\n🔧 Fix Steps:")
        print("1. Press Windows key + I")
        print("2. Go to Privacy & Security → Microphone")
        print("3. Turn ON 'Microphone access'")
        print("4. Turn ON 'Let apps access your microphone'")
        print("5. Find Python or Terminal and turn it ON")
        print("6. Set correct default microphone in Sound Settings")
        print("\nAlternative: Run dictation as Administrator")
    else:
        print("\n✅ Microphone working correctly!")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nThis usually means microphone access is denied.")
    print("Check Windows Privacy Settings for Microphone.")

print("\n" + "=" * 60)
input("\nPress Enter to exit...")
