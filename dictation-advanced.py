#!/usr/bin/env python3
"""
Advanced Dictation with Auto-Formatting
Supports GPT-based text formatting for long dictations
"""

import sounddevice as sd
import numpy as np
import keyboard
import pyperclip
import time
import json
import os
import tempfile
import threading
from faster_whisper import WhisperModel
from scipy.io.wavfile import write as wav_write

CONFIG_FILE = "config.json"

class AdvancedDictation:
    def __init__(self):
        self.sample_rate = 16000
        self.is_recording = False
        self.recording_thread = None
        
        # Load config
        self.config = self.load_config()
        self.hotkey = self.config.get("hotkey", "f15")
        self.language = self.config.get("language", None)
        self.model_size = self.config.get("model", "large-v3")
        self.compute_type = self.config.get("compute_type", "float16")
        
        # Audio settings
        self.microphone_gain = self.config.get("microphone_gain", 1.0)
        self.noise_threshold = self.config.get("noise_threshold", 0.01)
        self.min_duration = self.config.get("min_duration", 0.5)
        self.vad_filter = self.config.get("vad_filter", False)
        
        # Formatting settings
        self.auto_punctuation = self.config.get("auto_punctuation", True)
        self.auto_format = self.config.get("auto_format", False)
        self.format_style = self.config.get("format_style", "natural")
        self.format_prompt = self.config.get("format_prompt", None)
        
        # Whisper settings
        self.beam_size = self.config.get("beam_size", 5)
        self.best_of = self.config.get("best_of", 5)
        self.condition_on_previous_text = self.config.get("condition_on_previous_text", True)
        self.vad_parameters = self.config.get("vad_parameters", {})
        
        self.show_config()
        
        print("\nLoading model...")
        print(f"  Model: {self.model_size}")
        print(f"  Compute: {self.compute_type}")
        
        self.model = WhisperModel(
            self.model_size,
            device="cuda",
            compute_type=self.compute_type
        )
        print("✓ Model loaded\n")
        
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Config warning: {e}")
        return {}
    
    def show_config(self):
        print("=" * 60)
        print("Advanced Dictation System")
        print("=" * 60)
        print(f"\nConfiguration:")
        print(f"  Hotkey: {self.hotkey.upper()}")
        print(f"  Language: {self.language or 'Auto-detect'}")
        print(f"  Model: {self.model_size}")
        print(f"  Compute: {self.compute_type}")
        print(f"\nAudio:")
        print(f"  Microphone gain: {self.microphone_gain}x")
        print(f"  Noise threshold: {self.noise_threshold}")
        print(f"  VAD filter: {self.vad_filter}")
        print(f"\nFormatting:")
        print(f"  Auto-punctuation: {self.auto_punctuation}")
        print(f"  Auto-format (GPT): {self.auto_format}")
        print(f"  Format style: {self.format_style}")
        print(f"\nWhisper:")
        print(f"  Beam size: {self.beam_size}")
        print(f"  Best of: {self.best_of}")
    
    def apply_audio_effects(self, audio):
        """Apply gain and noise gate"""
        # Apply gain
        if self.microphone_gain != 1.0:
            audio = audio * self.microphone_gain
            # Prevent clipping
            audio = np.clip(audio, -1.0, 1.0)
        
        # Apply noise gate (simple version)
        if self.noise_threshold > 0:
            # This is a basic noise gate
            # For better results, use proper noise reduction
            pass
        
        return audio
    
    def record_audio(self):
        """Record audio with better error handling"""
        print(f"🔴 Recording... (gain: {self.microphone_gain}x)")
        
        all_audio = []
        chunk_duration = 0.05
        chunk_samples = int(chunk_duration * self.sample_rate)
        
        stream = sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='float32')
        stream.start()
        
        try:
            while self.is_recording:
                data, overflowed = stream.read(chunk_samples)
                if not overflowed:
                    all_audio.append(data.copy())
                time.sleep(0.001)
        finally:
            stream.stop()
            stream.close()
        
        if not all_audio:
            return None
        
        audio = np.concatenate(all_audio, axis=0)
        
        # Apply effects
        audio = self.apply_audio_effects(audio)
        
        duration = len(audio) / self.sample_rate
        print(f"✓ Recorded {duration:.2f}s")
        return audio
    
    def transcribe(self, audio):
        """Transcribe with full options"""
        temp_path = tempfile.mktemp(suffix='.wav')
        wav_write(temp_path, self.sample_rate, (audio * 32767).astype(np.int16))
        
        try:
            # Build transcribe options
            options = {
                'beam_size': self.beam_size,
                'best_of': self.best_of,
                'condition_on_previous_text': self.condition_on_previous_text,
                'language': self.language
            }
            
            if self.vad_filter:
                options['vad_filter'] = True
                if self.vad_parameters:
                    options['vad_parameters'] = self.vad_parameters
            
            segments, info = self.model.transcribe(temp_path, **options)
            
            # Combine segments
            text_parts = []
            for segment in segments:
                text = segment.text.strip()
                if text:
                    text_parts.append(text)
            
            text = " ".join(text_parts)
            
            return text, info
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def format_text(self, text):
        """Format text with GPT (placeholder for now)"""
        if not self.auto_format:
            return text
        
        # For now, just return the text
        # To add GPT formatting, you would:
        # 1. Call OpenAI API or local LLM
        # 2. Use the format_prompt or format_style
        # 3. Return formatted text
        
        print("  [Auto-format not implemented - requires API key]")
        print("  To enable: Set OPENAI_API_KEY and implement format_text()")
        return text
    
    def on_press(self, e):
        if not self.is_recording:
            self.is_recording = True
            self.recording_thread = threading.Thread(target=self.handle_recording)
            self.recording_thread.start()
    
    def on_release(self, e):
        self.is_recording = False
    
    def handle_recording(self):
        try:
            # Record
            audio = self.record_audio()
            
            if audio is None:
                print("⚠️ No audio recorded")
                return
            
            duration = len(audio) / self.sample_rate
            max_vol = np.max(np.abs(audio))
            
            print(f"  Duration: {duration:.2f}s | Volume: {max_vol:.3f}")
            
            # Validate
            if duration < self.min_duration:
                print(f"⚠️ Too short ({duration:.2f}s < {self.min_duration}s)")
                return
            
            if max_vol < self.noise_threshold:
                print(f"⚠️ Too quiet ({max_vol:.3f} < {self.noise_threshold})")
                return
            
            # Transcribe
            print("⏳ Transcribing...")
            text, info = self.transcribe(audio)
            
            if not text:
                print("⚠️ No speech detected")
                return
            
            # Format if enabled
            if self.auto_format and len(text) > 50:
                print("⏳ Formatting...")
                text = self.format_text(text)
            
            # Output
            print(f"✓ {text}")
            pyperclip.copy(text)
            time.sleep(0.05)
            keyboard.write(text)
            print(f"  → Typed!")
            
            if info.language:
                print(f"  [Detected: {info.language}]")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        print(f"\n{'='*60}")
        print("HOW TO USE:")
        print(f"  HOLD {self.hotkey.upper()} → SPEAK → RELEASE")
        print(f"  ESC to exit")
        print("="*60)
        print(f"\n✅ Ready!\n")
        
        keyboard.on_press_key(self.hotkey, self.on_press)
        keyboard.on_release_key(self.hotkey, self.on_release)
        keyboard.wait("esc")
        
        self.is_recording = False
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=2)
        
        print("\n👋 Stopped")

if __name__ == "__main__":
    try:
        app = AdvancedDictation()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter...")
