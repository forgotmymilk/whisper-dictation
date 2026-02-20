#!/usr/bin/env python3
"""
Simple Dictation - Fixed Version with Proper Hold Detection
"""

import sounddevice as sd
import numpy as np
import keyboard
import pyperclip
import time
import json
import os
from faster_whisper import WhisperModel
from scipy.io.wavfile import write as wav_write
import tempfile
import threading

# Configuration
CONFIG_FILE = "config.json"

class SimpleDictation:
    def __init__(self):
        self.sample_rate = 16000
        self.is_recording = False
        self.recording_thread = None
        
        # Load config
        self.config = self.load_config()
        self.hotkey = self.config.get("hotkey", "f15")
        self.language = self.config.get("language", None)
        
        print("=" * 60)
        print("Push-to-Talk Dictation - Fixed Version")
        print("=" * 60)
        print(f"\nHotkey: {self.hotkey.upper()}")
        
        print("\nLoading model...")
        self.model = WhisperModel(
            "large-v3",
            device="cuda",
            compute_type="float16"
        )
        print("✓ Model loaded")
        
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def record_audio(self):
        """Record audio until stopped"""
        print("🔴 Recording... (hold key and speak!)")
        
        all_audio = []
        chunk_duration = 0.05  # 50ms
        chunk_samples = int(chunk_duration * self.sample_rate)
        
        # Open stream
        stream = sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='float32')
        stream.start()
        
        try:
            while self.is_recording:
                # Read chunk
                data, overflowed = stream.read(chunk_samples)
                if not overflowed:
                    all_audio.append(data.copy())
                time.sleep(0.001)  # Small delay
        finally:
            stream.stop()
            stream.close()
        
        if not all_audio:
            return None
        
        # Combine
        audio = np.concatenate(all_audio, axis=0)
        duration = len(audio) / self.sample_rate
        
        print(f"✓ Recorded {duration:.2f}s")
        return audio
    
    def on_press(self, e):
        """Start recording"""
        if not self.is_recording:
            self.is_recording = True
            self.recording_thread = threading.Thread(target=self.handle_recording)
            self.recording_thread.start()
    
    def on_release(self, e):
        """Stop recording"""
        self.is_recording = False
    
    def handle_recording(self):
        """Recording and transcription worker"""
        try:
            # Record
            audio = self.record_audio()
            
            if audio is None:
                print("⚠️ No audio recorded")
                return
            
            duration = len(audio) / self.sample_rate
            max_vol = np.max(np.abs(audio))
            
            print(f"  Duration: {duration:.2f}s, Volume: {max_vol:.3f}")
            
            # Validate
            if duration < 0.5:
                print(f"⚠️ Too short ({duration:.2f}s) - hold key for at least 0.5s")
                return
            
            if max_vol < 0.01:
                print(f"⚠️ Too quiet ({max_vol:.3f}) - speak louder or check mic")
                return
            
            # Transcribe
            print("⏳ Transcribing...")
            temp_path = tempfile.mktemp(suffix='.wav')
            wav_write(temp_path, self.sample_rate, (audio * 32767).astype(np.int16))
            
            try:
                segments, info = self.model.transcribe(temp_path, beam_size=5, language=self.language)
                text = " ".join([s.text.strip() for s in segments])
                
                if text:
                    print(f"✓ {text}")
                    pyperclip.copy(text)
                    time.sleep(0.05)
                    keyboard.write(text)
                    print(f"  → Typed!")
                else:
                    print("⚠️ No speech detected")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def run(self):
        print(f"\n{'='*60}")
        print("INSTRUCTIONS:")
        print(f"  1. HOLD {self.hotkey.upper()} down (keep holding!)")
        print("  2. SPEAK while holding the key")
        print(f"  3. RELEASE when done speaking")
        print("  4. WAIT for transcription (1-2 seconds)")
        print("="*60)
        print(f"\nReady! Press and HOLD {self.hotkey.upper()} to dictate...\n")
        
        keyboard.on_press_key(self.hotkey, self.on_press)
        keyboard.on_release_key(self.hotkey, self.on_release)
        keyboard.wait("esc")
        
        self.is_recording = False
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=2)
        
        print("\n👋 Stopped")

if __name__ == "__main__":
    try:
        app = SimpleDictation()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter...")
