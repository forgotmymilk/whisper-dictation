#!/usr/bin/env python3
"""
Debug version to test key detection timing
"""

import keyboard
import time
import sounddevice as sd
import numpy as np

print("=" * 60)
print("KEY DETECTION DEBUG")
print("=" * 60)
print("\nThis will show exactly when keys are pressed and released")
print("Hold F15 for 3 seconds, then release...\n")

press_time = None
release_time = None
is_pressed = False

def on_press(e):
    global press_time, is_pressed
    if not is_pressed:
        press_time = time.time()
        is_pressed = True
        print(f"🔴 PRESSED at {press_time:.3f}")

def on_release(e):
    global release_time, is_pressed
    if is_pressed:
        release_time = time.time()
        is_pressed = False
        duration = release_time - press_time if press_time else 0
        print(f"✓ RELEASED at {release_time:.3f} (held for {duration:.3f}s)")

keyboard.on_press_key("f15", on_press)
keyboard.on_release_key("f15", on_release)

print("Listening for F15... (Press ESC to exit)")
print("-" * 60)

keyboard.wait("esc")

print("\n" + "=" * 60)
if press_time and release_time:
    total_duration = release_time - press_time
    print(f"Total hold time: {total_duration:.3f} seconds")
    if total_duration < 0.5:
        print("\n⚠️ WARNING: Key released too quickly!")
        print("   Hold the key for at least 1-2 seconds while speaking")
else:
    print("No key events detected")
print("=" * 60)
