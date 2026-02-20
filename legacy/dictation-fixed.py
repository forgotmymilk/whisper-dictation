#!/usr/bin/env python3
"""
Push-to-Talk Real-Time Dictation - FIXED VERSION
HOLD hotkey to record, RELEASE to transcribe and type

HOTKEY: F15 (change in config.json)
X-Mouse: Configure mouse button to send {F15}

Controls:
    HOLD F15 → Speak → RELEASE → Auto-type transcription
    ESC → Exit
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
DEFAULT_HOTKEY = "f15"
CONFIG_FILE = "config.json"

class WhisperDictation:
    def __init__(self):
        self.is_recording = False
        self.audio_buffer = []
        self.sample_rate = 16000
        self.recording_thread = None
        self.stream = None
        
        # Load config
        self.config = self.load_config()
        self.hotkey = self.config.get("hotkey", DEFAULT_HOTKEY)
        self.language = self.config.get("language", None)
        self.model_size = self.config.get("model", "large-v3")
        self.compute_type = self.config.get("compute_type", "float16")
        
        print("=" * 60)
        print("Push-to-Talk Dictation System")
        print("=" * 60)
        print(f"\nConfiguration:")
        print(f"  Hotkey: {self.hotkey.upper()}")
        print(f"  Model: {self.model_size}")
        print(f"  Language: {self.language or 'Auto-detect'}")
        print(f"  Compute: {self.compute_type}")
        
        print(f"\nLoading {self.model_size} model...")
        print("(This may take a moment...)")
        
        self.model = WhisperModel(
            self.model_size,
            device="cuda",
            compute_type=self.compute_type
        )
        
        print("Model loaded! GPU acceleration active.")
        print(f"\nInstructions:")
        print(f"  HOLD '{self.hotkey.upper()}' → Speak → RELEASE to transcribe")
        print(f"  Press 'ESC' to exit")
        print("-" * 60)
        
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load config.json: {e}")
        return {}
    
    def audio_callback(self, indata, frames, time_info, status):
        """Capture audio while recording"""
        if self.is_recording:
            self.audio_buffer.append(indata.copy())
    
    def start_recording(self):
        """Begin recording"""
        if self.is_recording:
            return
        
        self.audio_buffer = []
        self.is_recording = True
        print("\n🔴 Recording... (speak now)")
    
    def stop_recording(self):
        """Stop and transcribe"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        
        # Small delay to ensure all audio is captured
        time.sleep(0.1)
        
        if not self.audio_buffer:
            print("⚠️ No audio captured (buffer empty)")
            return
        
        # Concatenate audio
        audio_data = np.concatenate(self.audio_buffer, axis=0)
        duration = len(audio_data) / self.sample_rate
        
        if duration < 0.5:
            print(f"⚠️ Recording too short ({duration:.1f}s) - hold key longer")
            return
        
        print(f"⏳ Processing {duration:.1f}s of audio...")
        
        # Save to temp file
        temp_path = os.path.join(tempfile.gettempdir(), "dictation_temp.wav")
        try:
            wav_write(temp_path, self.sample_rate, (audio_data * 32767).astype(np.int16))
            
            # Transcribe
            segments, info = self.model.transcribe(
                temp_path,
                beam_size=5,
                best_of=5,
                condition_on_previous_text=True,
                language=self.language
            )
            
            text = " ".join([segment.text.strip() for segment in segments])
            
            if text:
                print(f"✓ Transcribed: {text}")
                pyperclip.copy(text)
                time.sleep(0.05)
                keyboard.write(text)
                print(f"   → Typed into active window")
            else:
                print("⚠️ No speech detected")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def run(self):
        """Main loop"""
        # Start audio stream continuously
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=self.audio_callback,
            blocksize=1024
        )
        
        self.stream.start()
        
        try:
            # Register hotkeys
            keyboard.on_press_key(self.hotkey, lambda _: self.start_recording())
            keyboard.on_release_key(self.hotkey, lambda _: self.stop_recording())
            
            print(f"\n✅ Ready! Hold {self.hotkey.upper()} to dictate...")
            
            # Wait for ESC
            keyboard.wait("esc")
            
        finally:
            self.stream.stop()
            self.stream.close()
        
        print("\n👋 Dictation stopped.")

def test_microphone():
    """Quick microphone test"""
    print("Testing microphone...")
    print("Speak now for 3 seconds...")
    
    try:
        recording = sd.rec(int(3 * 16000), samplerate=16000, channels=1, dtype='float32')
        sd.wait()
        
        max_val = np.max(np.abs(recording))
        if max_val > 0.01:
            print(f"✓ Microphone OK (volume: {max_val:.3f})")
            return True
        else:
            print("⚠️ Microphone volume too low")
            return False
    except Exception as e:
        print(f"❌ Microphone error: {e}")
        return False

if __name__ == "__main__":
    try:
        if not test_microphone():
            print("\nPlease check microphone settings and try again.")
            input("Press Enter to exit...")
            exit(1)
        
        dictation = WhisperDictation()
        dictation.run()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("\nPress Enter to exit...")
