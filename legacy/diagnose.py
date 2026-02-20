#!/usr/bin/env python3
"""
Diagnostic script for dictation issues
Tests each component step by step
"""

import sounddevice as sd
import numpy as np
import keyboard
import time

print("=" * 60)
print("DIAGNOSTIC: Dictation System")
print("=" * 60)

# Test 1: Audio Device
print("\n[TEST 1] Audio Device Configuration")
print("-" * 60)
try:
    default_input = sd.query_devices(kind='input')
    print(f"✓ Default input: {default_input['name']}")
    print(f"  Index: {default_input['index']}")
    print(f"  Sample rate: {default_input['default_samplerate']}")
    print(f"  Channels: {default_input['max_input_channels']}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Keyboard Hotkey
print("\n[TEST 2] Hotkey Detection")
print("-" * 60)
print("Testing F15 key detection...")
print("Press and hold F15 for 2 seconds, then release...")

key_pressed = False
key_released = False

def on_press(e):
    global key_pressed
    if not key_pressed:
        print("  ✓ Key PRESSED detected")
        key_pressed = True

def on_release(e):
    global key_released
    if not key_released:
        print("  ✓ Key RELEASED detected")
        key_released = True

keyboard.on_press_key("f15", on_press)
keyboard.on_release_key("f15", on_release)

time.sleep(3)
keyboard.unhook_all()

if not key_pressed:
    print("  ❌ F15 not detected! Check X-Mouse configuration")
else:
    print("  ✓ Hotkey working correctly")

# Test 3: Audio Stream Callback
print("\n[TEST 3] Audio Stream Recording")
print("-" * 60)
print("Recording for 3 seconds with callback method...")

audio_buffer = []
is_recording = True

def callback(indata, frames, time_info, status):
    if is_recording:
        audio_buffer.append(indata.copy())
        if len(audio_buffer) % 10 == 0:
            print(f"  Captured {len(audio_buffer)} chunks...", end='\r')

stream = sd.InputStream(
    samplerate=16000,
    channels=1,
    callback=callback,
    blocksize=1024
)

stream.start()
time.sleep(3)
is_recording = False
stream.stop()
stream.close()

print(f"\n  Total chunks captured: {len(audio_buffer)}")

if audio_buffer:
    audio_data = np.concatenate(audio_buffer, axis=0)
    max_val = np.max(np.abs(audio_data))
    print(f"  Max amplitude: {max_val:.4f}")
    
    if max_val > 0.01:
        print("  ✓ Audio captured successfully")
    else:
        print("  ⚠️ Audio captured but very low volume")
else:
    print("  ❌ No audio captured - callback not working")

# Test 4: Simulated Push-to-Talk
print("\n[TEST 4] Push-to-Talk Simulation")
print("-" * 60)
print("This test simulates the exact dictation workflow")
print("\n👉 Hold F15 and speak for 2 seconds, then release")

recording_buffer = []
is_recording_ptt = False

def ptt_callback(indata, frames, time_info, status):
    if is_recording_ptt:
        recording_buffer.append(indata.copy())

def ptt_press(e):
    global is_recording_ptt, recording_buffer
    is_recording_ptt = True
    recording_buffer = []
    print("\n🔴 Recording started...")

def ptt_release(e):
    global is_recording_ptt
    is_recording_ptt = False
    print("\n⏳ Processing...")

stream2 = sd.InputStream(
    samplerate=16000,
    channels=1,
    callback=ptt_callback,
    blocksize=1024
)

stream2.start()
keyboard.on_press_key("f15", ptt_press)
keyboard.on_release_key("f15", ptt_release)

print("(Waiting for you to press F15...)")
time.sleep(5)

keyboard.unhook_all()
stream2.stop()
stream2.close()

print(f"\nChunks captured: {len(recording_buffer)}")

if recording_buffer:
    audio = np.concatenate(recording_buffer, axis=0)
    duration = len(audio) / 16000
    max_val = np.max(np.abs(audio))
    print(f"Duration: {duration:.1f}s")
    print(f"Max amplitude: {max_val:.4f}")
    
    if duration > 0.5 and max_val > 0.01:
        print("\n✅ PUSH-TO-TALK WORKING!")
        print("The dictation system should work. Try start-dictation.bat")
    else:
        print("\n❌ Issue detected - check duration and volume")
else:
    print("\n❌ No audio captured during PTT test")
    print("Possible causes:")
    print("  1. Hotkey not triggering properly")
    print("  2. Audio stream not in callback mode")
    print("  3. Permission issue")

print("\n" + "=" * 60)
input("\nPress Enter to exit...")
