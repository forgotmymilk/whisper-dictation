#!/usr/bin/env python3
"""
Push-to-Talk Real-Time Dictation with Configurable Hotkey

HOTKEY CONFIGURATION:
Edit config.json or change the hotkey variable below.
Recommended for X-Mouse Button Control: F15, F16, F17, F18, F19, F20

X-Mouse Setup:
1. Open X-Mouse Button Control
2. Select your mouse button
3. Choose "Simulated Keys"
4. Enter: {F15} (or whatever hotkey you set below)
5. Set as "Pressed" for push-to-talk behavior

Usage:
    python dictation.py
    
    HOLD configured hotkey → Speak → RELEASE to transcribe
    Press 'ESC' to exit
"""

import sounddevice as sd
import numpy as np
import keyboard
import pyperclip
import time
import threading
import json
import os
from faster_whisper import WhisperModel
from scipy.io.wavfile import write as wav_write
import tempfile

# ============ CONFIGURATION ============
# Default hotkey - change this or create config.json
# Recommended X-Mouse keys: F15, F16, F17, F18, F19, F20
# Other options: "ctrl+shift+d", "insert", "pause", "scroll lock"
DEFAULT_HOTKEY = "f15"

CONFIG_FILE = "config.json"
# ======================================

class WhisperDictation:
    def __init__(self):
        self.is_recording = False
        self.audio_buffer = []
        self.sample_rate = 16000
        self.stream = None
        
        # Load or create config
        self.config = self.load_config()
        self.hotkey = self.config.get("hotkey", DEFAULT_HOTKEY)
        self.language = self.config.get("language", None)  # None = auto-detect
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
        
        # Load model with GPU optimization
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
        """Load configuration from config.json"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load config.json: {e}")
        return {}
    
    def save_config(self):
        """Save current configuration"""
        config = {
            "hotkey": self.hotkey,
            "language": self.language,
            "model": self.model_size,
            "compute_type": self.compute_type
        }
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config.json: {e}")
        
    def audio_callback(self, indata, frames, time_info, status):
        """Capture audio while recording"""
        if self.is_recording:
            self.audio_buffer.append(indata.copy())
    
    def start_recording(self):
        """Begin recording audio"""
        if self.is_recording:
            return
            
        self.audio_buffer = []
        self.is_recording = True
        print("\n🔴 Recording... (speak now)")
        
    def stop_recording(self):
        """Stop recording and transcribe"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        
        # Wait a moment for final audio chunks
        time.sleep(0.1)
        
        if not self.audio_buffer:
            print("⚠️ No audio captured - hold the key longer (minimum 0.5 seconds)")
            return
        
        # Concatenate all audio chunks
        audio_data = np.concatenate(self.audio_buffer, axis=0)
        duration = len(audio_data) / self.sample_rate
        
        # Check minimum duration
        if duration < 0.5:
            print(f"⚠️ Recording too short ({duration:.1f}s) - hold key for at least 0.5 seconds")
            return
        
        print(f"⏳ Processing {duration:.1f}s of audio...")
        
        # Save to temporary WAV file
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
            
            # Combine all segments
            text = " ".join([segment.text.strip() for segment in segments])
            
            if text:
                print(f"✓ Transcribed: {text}")
                
                # Copy to clipboard
                pyperclip.copy(text)
                
                # Auto-type into active window
                time.sleep(0.05)
                keyboard.write(text)
                
                print(f"   → Typed into active window")
            else:
                print("⚠️ No speech detected")
                
        except Exception as e:
            print(f"❌ Transcription error: {e}")
        
        finally:
            # Cleanup
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def run(self):
        """Main loop - handles hotkeys and recording"""
        # Start audio stream continuously (not in a context manager)
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
            
            print(f"\n✅ Ready! HOLD '{self.hotkey.upper()}' to dictate...")
            
            # Keep running until ESC
            keyboard.wait("esc")
            
        finally:
            self.stream.stop()
            self.stream.close()
        
        print("\n👋 Dictation system stopped.")

def test_microphone():
    """Quick test to verify microphone is working"""
    print("Testing microphone...")
    print("Speak now for 3 seconds...")
    
    try:
        recording = sd.rec(int(3 * 16000), samplerate=16000, channels=1, dtype='float32')
        sd.wait()
        
        max_val = np.max(np.abs(recording))
        mean_val = np.mean(np.abs(recording))
        
        if max_val > 0.01:
            print(f"✓ Microphone detected! Volume: {max_val:.3f}")
            return True
        else:
            print("⚠️ Microphone volume too low")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    try:
        # Test microphone first
        if not test_microphone():
            print("\nPlease check your microphone and try again.")
            input("Press Enter to exit...")
            exit(1)
        
        # Start dictation
        dictation = WhisperDictation()
        dictation.run()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Run install.bat first")
        print("2. Check microphone is connected and enabled")
        print("3. For CPU mode, change device='cuda' to device='cpu'")
        print("4. Check config.json for correct hotkey settings")
        input("\nPress Enter to exit...")
