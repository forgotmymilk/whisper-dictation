#!/usr/bin/env python3
"""
Universal Whisper Dictation - Portable & User-Friendly

Features:
- Chinese/English/Mixed input with smart formatting
- Auto punctuation for both languages
- Device auto-detection (GPU/CPU)
- Portable configuration
- Easy setup for non-technical users

Usage:
    python dictation-universal.py
"""

import sounddevice as sd
import numpy as np
import keyboard
import pyperclip
import time
import json
import os
import re
import platform
import subprocess
from pathlib import Path
from faster_whisper import WhisperModel
from scipy.io.wavfile import write as wav_write
import tempfile

# ============ CONFIGURATION ============
DEFAULT_CONFIG = {
    "hotkey": "f15",
    "language": None,
    "model": "auto",  # 'auto' will detect based on device capability
    "compute_type": "auto",  # 'auto' will detect GPU/CPU
    "device": "auto",  # 'auto', 'cuda', 'cpu'
    "enable_punctuation": True,
    "enable_formatting": True,
    "enable_capitalization": True,
    "max_line_length": 80,
    "output_mode": "type",  # 'type', 'clipboard', 'both'
    "audio_threshold": 0.01,
    "initial_prompt": None,
    "user_profile": {
        "name": "",
        "primary_language": "auto",  # 'auto', 'zh', 'en', 'mixed'
        "formality": "casual",  # 'casual', 'formal', 'business'
        "common_phrases": []
    }
}

CONFIG_FILE = "user-config.json"
DEVICE_PROFILE_FILE = "device-profile.json"

# Language detection patterns
ENGLISH_PATTERN = re.compile(r'^[a-zA-Z\s\.,!?;:\-\'"()[\]{}]+$')
CHINESE_PATTERN = re.compile(r'[\u4e00-\u9fff]')
# ======================================

class DeviceProfiler:
    """自动检测设备能力并推荐最佳配置"""
    
    @staticmethod
    def detect_gpu():
        """检测GPU类型和能力"""
        try:
            import torch
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                
                return {
                    "available": True,
                    "name": gpu_name,
                    "vram_gb": vram_gb,
                    "cuda_version": torch.version.cuda,
                    "compute_capability": torch.cuda.get_device_capability(0)
                }
        except:
            pass
        return {"available": False, "name": "CPU Only", "vram_gb": 0}
    
    @staticmethod
    def detect_audio_devices():
        """检测可用音频设备"""
        try:
            devices = sd.query_devices()
            input_devices = [d for d in devices if d['max_input_channels'] > 0]
            return {
                "count": len(input_devices),
                "default": sd.query_devices(kind='input'),
                "all": input_devices
            }
        except:
            return {"count": 0, "default": None, "all": []}
    
    @staticmethod
    def recommend_config(gpu_info):
        """根据硬件推荐配置"""
        if not gpu_info["available"]:
            return {
                "model": "base",
                "compute_type": "int8",
                "device": "cpu",
                "beam_size": 3,
                "note": "Running in CPU mode. Consider using 'tiny' or 'base' model for better speed."
            }
        
        vram = gpu_info["vram_gb"]
        
        if vram >= 10:  # High-end GPU (RTX 4070+, 3080+)
            return {
                "model": "large-v3",
                "compute_type": "float16",
                "device": "cuda",
                "beam_size": 5,
                "note": "High-performance mode activated. Best accuracy for mixed Chinese-English."
            }
        elif vram >= 5:  # Mid-range GPU (RTX 3060, 2060)
            return {
                "model": "medium",
                "compute_type": "float16",
                "device": "cuda",
                "beam_size": 5,
                "note": "Balanced mode. Good accuracy with reasonable speed."
            }
        elif vram >= 2:  # Entry GPU (GTX 1650, etc.)
            return {
                "model": "small",
                "compute_type": "int8",
                "device": "cuda",
                "beam_size": 3,
                "note": "Economy GPU mode. Consider 'base' model for better accuracy."
            }
        else:  # Low VRAM or integrated graphics
            return {
                "model": "base",
                "compute_type": "int8",
                "device": "cuda",
                "beam_size": 3,
                "note": "Low VRAM mode. Using quantized model."
            }
    
    @staticmethod
    def create_profile():
        """创建设备配置文件"""
        print("🔍 Analyzing your system...")
        
        gpu_info = DeviceProfiler.detect_gpu()
        audio_info = DeviceProfiler.detect_audio_devices()
        recommendations = DeviceProfiler.recommend_config(gpu_info)
        
        profile = {
            "system": {
                "platform": platform.system(),
                "python_version": platform.python_version(),
            },
            "gpu": gpu_info,
            "audio": audio_info,
            "recommendations": recommendations,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Save device profile
        with open(DEVICE_PROFILE_FILE, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
        
        return profile


class SmartFormatter:
    """Universal Text Formatter - Chinese & English"""
    
    # Chinese punctuation rules
    CN_PARTICLES = {
        '啊': '！', '呀': '！', '哇': '！', '啦': '！', '呢': '？', 
        '吧': '？', '吗': '？', '么': '？', '嘛': '！', '哦': '。', '诶': '，',
    }
    
    CN_SENTENCE_STARTERS = ['首先', '其次', '然后', '接着', '最后', '总之', '所以', '因此', '但是', '然而', '不过', '第一', '第二', '第三']
    CN_CONNECTORS = ['而且', '并且', '或者', '还是', '因为', '由于', '虽然', '尽管']
    
    # English formatting rules
    EN_SENTENCE_ENDERS = ['.', '!', '?']
    EN_COMMON_ABBREVIATIONS = ['Mr.', 'Mrs.', 'Dr.', 'Prof.', 'Inc.', 'Ltd.', 'Jr.', 'Sr.', 'vs.', 'etc.', 'i.e.', 'e.g.']
    
    @staticmethod
    def detect_language(text):
        """检测文本主要语言"""
        cn_chars = len(CHINESE_PATTERN.findall(text))
        en_chars = len(re.findall(r'[a-zA-Z]', text))
        
        if cn_chars > en_chars:
            return 'chinese' if cn_chars > 5 else 'mixed'
        elif en_chars > cn_chars:
            return 'english' if en_chars > 5 else 'mixed'
        return 'mixed'
    
    @staticmethod
    def format_text(text, lang=None, enable_punct=True, enable_format=True, enable_cap=True):
        """Universal text formatting"""
        if not text:
            return text
        
        if lang is None:
            lang = SmartFormatter.detect_language(text)
        
        original = text.strip()
        
        # Step 1: Add punctuation
        if enable_punct:
            if lang in ['chinese', 'mixed']:
                text = SmartFormatter.add_chinese_punctuation(text)
            if lang in ['english', 'mixed']:
                text = SmartFormatter.add_english_punctuation(text)
        
        # Step 2: Capitalization (English)
        if enable_cap and lang in ['english', 'mixed']:
            text = SmartFormatter.capitalize_english(text)
        
        # Step 3: Layout formatting
        if enable_format:
            text = SmartFormatter.format_layout(text, lang)
        
        return text
    
    @staticmethod
    def add_chinese_punctuation(text):
        """Add punctuation for Chinese text"""
        if not CHINESE_PATTERN.search(text):
            return text
        
        # Check if already has sufficient punctuation
        cn_chars = len(CHINESE_PATTERN.findall(text))
        punct_count = len(re.findall(r'[，。？！；：]', text))
        if cn_chars > 0 and punct_count >= cn_chars / 15:
            return text
        
        # Add particles punctuation
        for particle, punct in SmartFormatter.CN_PARTICLES.items():
            pattern = f'{particle}(?![，。？！,\.?!])'
            text = re.sub(pattern, f'{particle}{punct}', text)
        
        # Add sentence starter punctuation
        for starter in SmartFormatter.CN_SENTENCE_STARTERS:
            pattern = f'(?<![，。？！,\.?!\n]){starter}'
            text = re.sub(pattern, f'。{starter}', text)
        
        # Add connector punctuation
        for connector in SmartFormatter.CN_CONNECTORS:
            pattern = f'(?<![，。？！,\.?!\n]){connector}'
            text = re.sub(pattern, f'，{connector}', text)
        
        # Clean and finalize
        text = SmartFormatter.clean_punctuation(text)
        
        if text and text[-1] not in '，。？！,\.?!':
            text += '。'
        
        return text
    
    @staticmethod
    def add_english_punctuation(text):
        """Add punctuation for English text"""
        if not re.search(r'[a-zA-Z]', text):
            return text
        
        # Check if already has sufficient punctuation
        sentences = len(re.findall(r'[a-zA-Z][\.!?]', text))
        words = len(re.findall(r'[a-zA-Z]+', text))
        if words > 0 and sentences >= words / 20:
            return text
        
        # Split into potential sentences
        parts = re.split(r'(\s+(?:and|but|or|so|because|however|therefore|moreover|furthermore)\s+)', text, flags=re.IGNORECASE)
        
        result = []
        for i, part in enumerate(parts):
            if not part.strip():
                result.append(part)
                continue
            
            # Check if it's a connector
            if re.match(r'^\s+(?:and|but|or)\s+$', part, re.IGNORECASE) and i > 0:
                # Add comma before connector if not present
                if result and not result[-1].rstrip()[-1:] in '.,!?;:': 
                    result[-1] = result[-1].rstrip() + ','
                result.append(part)
            elif re.match(r'^\s+(?:so|because|however|therefore)\s+$', part, re.IGNORECASE) and i > 0:
                # Stronger separation for these
                if result and not result[-1].rstrip()[-1:] in '.!?':
                    result[-1] = result[-1].rstrip() + '.'
                result.append(part)
            else:
                result.append(part)
        
        text = ''.join(result)
        
        # Ensure sentence ends with punctuation
        text = text.strip()
        if text and text[-1] not in '.!?':
            # Check if it ends with abbreviation
            if not any(text.endswith(abbr) for abbr in SmartFormatter.EN_COMMON_ABBREVIATIONS):
                text += '.'
        
        return text
    
    @staticmethod
    def capitalize_english(text):
        """Smart capitalization for English"""
        # Split into sentences
        sentences = re.split(r'([.!?]\s+)', text)
        result = []
        
        for i, sent in enumerate(sentences):
            if not sent.strip():
                result.append(sent)
                continue
            
            # Check if this is a separator
            if re.match(r'^[.!?]\s+$', sent):
                result.append(sent)
                continue
            
            # Capitalize first letter of sentence
            words = sent.split()
            if words:
                words[0] = words[0].capitalize()
                
                # Capitalize 'I'
                words = ['I' if w.lower() == 'i' and (i == 0 or not w.isupper()) else w for w in words]
                
                result.append(' '.join(words))
            else:
                result.append(sent)
        
        return ''.join(result)
    
    @staticmethod
    def format_layout(text, lang='mixed', max_length=80):
        """Format layout for readability"""
        if not text:
            return text
        
        # Optimize spacing between languages
        text = SmartFormatter.optimize_spacing(text)
        
        # Paragraph segmentation
        text = SmartFormatter.paragraph_segmentation(text, lang)
        
        # Line breaking for long text
        text = SmartFormatter.break_long_lines(text, max_length)
        
        # Clean up
        text = re.sub(r'  +', ' ', text)
        text = re.sub(r'\n\n\n+', '\n\n', text)
        
        return text.strip()
    
    @staticmethod
    def optimize_spacing(text):
        """Optimize spacing between Chinese and English"""
        # Add space between Chinese and English/numbers
        text = re.sub(r'([\u4e00-\u9fff])([a-zA-Z0-9])', r'\1 \2', text)
        text = re.sub(r'([a-zA-Z0-9])([\u4e00-\u9fff])', r'\1 \2', text)
        
        # Clean multiple spaces
        text = re.sub(r'  +', ' ', text)
        
        return text
    
    @staticmethod
    def paragraph_segmentation(text, lang):
        """Segment into paragraphs"""
        # Chinese paragraph markers
        cn_markers = ['首先', '其次', '第一', '第二', '第三', '最后', '总结', '总之', '综上']
        # English paragraph markers
        en_markers = ['First', 'Second', 'Third', 'Finally', 'In conclusion', 'To summarize', 'Overall']
        
        markers = cn_markers if lang == 'chinese' else en_markers if lang == 'english' else cn_markers + en_markers
        
        for marker in markers:
            pattern = rf'(?<!^)(?<![\n])\s*{marker}\b'
            text = re.sub(pattern, f'\n{marker}', text)
        
        return text
    
    @staticmethod
    def break_long_lines(text, max_length):
        """Break long lines for readability"""
        lines = text.split('\n')
        result = []
        
        for line in lines:
            if len(line) <= max_length:
                result.append(line)
                continue
            
            # Break at sentence boundaries
            sentences = re.split(r'([.!?。！？])', line)
            current = ""
            
            for sent in sentences:
                if len(current) + len(sent) > max_length and current:
                    result.append(current)
                    current = sent
                else:
                    current += sent
            
            if current:
                result.append(current)
        
        return '\n'.join(result)
    
    @staticmethod
    def clean_punctuation(text):
        """Clean duplicate and misplaced punctuation"""
        # Merge duplicate punctuation
        text = re.sub(r'[，,]{2,}', '，', text)
        text = re.sub(r'[。.]{2,}', '。', text)
        text = re.sub(r'[！!]{2,}', '！', text)
        text = re.sub(r'[？?]{2,}', '？', text)
        
        # Fix sequences
        text = re.sub(r'，。', '。', text)
        text = re.sub(r'。，', '。', text)
        
        return text


class SetupWizard:
    """Setup wizard for non-technical users"""
    
    @staticmethod
    def run():
        """Interactive setup"""
        print("\n" + "="*60)
        print("🎯 Welcome to Universal Whisper Dictation Setup")
        print("="*60)
        
        config = DEFAULT_CONFIG.copy()
        
        # Device detection
        print("\n📊 Step 1: Device Detection")
        profile = DeviceProfiler.create_profile()
        
        gpu_info = profile["gpu"]
        if gpu_info["available"]:
            print(f"   ✓ GPU detected: {gpu_info['name']}")
            print(f"   ✓ VRAM: {gpu_info['vram_gb']:.1f} GB")
        else:
            print("   ℹ️ No GPU detected, will use CPU mode")
        
        rec = profile["recommendations"]
        print(f"\n   Recommended: {rec['model']} model ({rec['note']})")
        
        # Apply recommendations
        config["model"] = rec["model"]
        config["compute_type"] = rec["compute_type"]
        config["device"] = rec["device"]
        
        # User preferences
        print("\n🎨 Step 2: Personal Preferences")
        
        # Primary language
        print("\n   Primary language usage:")
        print("   1. Chinese (中文)")
        print("   2. English")
        print("   3. Mixed (Chinese + English)")
        print("   4. Auto-detect")
        choice = input("   Select (1-4) [4]: ").strip() or "4"
        lang_map = {"1": "zh", "2": "en", "3": "mixed", "4": "auto"}
        config["user_profile"]["primary_language"] = lang_map.get(choice, "auto")
        
        # Formality
        print("\n   Text style:")
        print("   1. Casual (适合聊天、日常)")
        print("   2. Formal (适合工作邮件)")
        print("   3. Business (适合商务场景)")
        choice = input("   Select (1-3) [1]: ").strip() or "1"
        formality_map = {"1": "casual", "2": "formal", "3": "business"}
        config["user_profile"]["formality"] = formality_map.get(choice, "casual")
        
        # Hotkey
        print("\n⌨️  Step 3: Hotkey Configuration")
        print("   Recommended for mouse buttons: F15, F16, F17, F18, F19, F20")
        print("   Other options: ctrl+shift+d, insert, pause")
        hotkey = input(f"   Enter hotkey [{config['hotkey']}]: ").strip()
        if hotkey:
            config["hotkey"] = hotkey
        
        # Features
        print("\n⚙️  Step 4: Features")
        
        punct = input("   Enable auto-punctuation? (y/n) [y]: ").strip().lower()
        config["enable_punctuation"] = punct != 'n'
        
        fmt = input("   Enable smart formatting? (y/n) [y]: ").strip().lower()
        config["enable_formatting"] = fmt != 'n'
        
        cap = input("   Enable auto-capitalization? (y/n) [y]: ").strip().lower()
        config["enable_capitalization"] = cap != 'n'
        
        # Output mode
        print("\n📤 Step 5: Output Mode")
        print("   1. Type directly into active window")
        print("   2. Copy to clipboard only")
        print("   3. Both type and copy to clipboard")
        choice = input("   Select (1-3) [1]: ").strip() or "1"
        mode_map = {"1": "type", "2": "clipboard", "3": "both"}
        config["output_mode"] = mode_map.get(choice, "type")
        
        # Save configuration
        print("\n💾 Saving configuration...")
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("\n" + "="*60)
        print("✅ Setup complete!")
        print("="*60)
        print(f"\nConfiguration saved to: {CONFIG_FILE}")
        print(f"Device profile saved to: {DEVICE_PROFILE_FILE}")
        print("\nYou can run the setup again anytime by deleting these files.")
        print("\nPress Enter to start dictation...")
        input()
        
        return config


class WhisperDictation:
    """Main dictation class"""
    
    def __init__(self, config):
        self.config = config
        self.is_recording = False
        self.audio_buffer = []
        self.sample_rate = 16000
        self.stream = None
        self.formatter = SmartFormatter()
        self.model = None
        
        # Load settings
        self.hotkey = config.get("hotkey", "f15")
        self.language = config.get("language")
        self.model_size = config.get("model", "base")
        self.compute_type = config.get("compute_type", "int8")
        self.device = config.get("device", "cpu")
        self.enable_punct = config.get("enable_punctuation", True)
        self.enable_format = config.get("enable_formatting", True)
        self.enable_cap = config.get("enable_capitalization", True)
        self.output_mode = config.get("output_mode", "type")
        self.audio_threshold = config.get("audio_threshold", 0.01)
        self.initial_prompt = config.get("initial_prompt")
        self.user_profile = config.get("user_profile", {})
        
        self._print_banner()
        self._load_model()
    
    def _print_banner(self):
        """Print startup banner"""
        print("\n" + "="*60)
        print("🎤 Universal Whisper Dictation")
        print("="*60)
        print(f"\n📋 Configuration:")
        print(f"   Hotkey: {self.hotkey.upper()}")
        print(f"   Model: {self.model_size}")
        print(f"   Device: {self.device.upper()}")
        print(f"   Language: {self.language or 'Auto-detect'}")
        print(f"   Auto-punctuation: {'✓' if self.enable_punct else '✗'}")
        print(f"   Smart formatting: {'✓' if self.enable_format else '✗'}")
        print(f"   Auto-capitalization: {'✓' if self.enable_cap else '✗'}")
        print(f"   Output: {self.output_mode}")
        print("\n" + "-"*60)
        print(f"🎯 Instructions:")
        print(f"   HOLD '{self.hotkey.upper()}' → Speak → RELEASE")
        print(f"   Press 'ESC' to exit")
        print("-"*60 + "\n")
    
    def _load_model(self):
        """Load Whisper model"""
        print(f"⏳ Loading {self.model_size} model...")
        print("   (First run may download model files)")
        
        try:
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
            print(f"✅ Model loaded successfully!\n")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            print("   Falling back to CPU mode with base model...")
            self.model = WhisperModel("base", device="cpu", compute_type="int8")
            print(f"✅ Fallback model loaded!\n")
    
    def audio_callback(self, indata, frames, time_info, status):
        """Audio capture callback"""
        if self.is_recording:
            self.audio_buffer.append(indata.copy())
    
    def start_recording(self):
        """Start recording"""
        if self.is_recording:
            return
        
        self.audio_buffer = []
        self.is_recording = True
        print("🔴 Recording... (speak now)")
    
    def stop_recording(self):
        """Stop and process recording"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        time.sleep(0.1)
        
        if not self.audio_buffer:
            print("⚠️  No audio captured (hold key longer)\n")
            return
        
        audio_data = np.concatenate(self.audio_buffer, axis=0)
        duration = len(audio_data) / self.sample_rate
        
        if duration < 0.5:
            print(f"⚠️  Recording too short ({duration:.1f}s)\n")
            return
        
        print(f"⏳ Processing {duration:.1f}s...", end=" ")
        
        temp_path = os.path.join(tempfile.gettempdir(), "dictation_temp.wav")
        
        try:
            wav_write(temp_path, self.sample_rate, (audio_data * 32767).astype(np.int16))
            
            # Transcription options
            options = {
                "beam_size": 5 if self.model_size in ["large-v3", "large-v2", "large"] else 3,
                "best_of": 5 if self.model_size in ["large-v3", "large-v2", "large"] else 3,
                "condition_on_previous_text": True,
                "language": self.language,
                "vad_filter": True,
                "vad_parameters": {
                    "min_silence_duration_ms": 300,
                    "max_speech_duration_s": duration + 1
                }
            }
            
            if self.initial_prompt:
                options["initial_prompt"] = self.initial_prompt
            
            segments, info = self.model.transcribe(temp_path, **options)
            text = " ".join([segment.text.strip() for segment in segments])
            
            if text:
                # Detect language and format
                lang = self.formatter.detect_language(text)
                formatted = self.formatter.format_text(
                    text, 
                    lang=lang,
                    enable_punct=self.enable_punct,
                    enable_format=self.enable_format,
                    enable_cap=self.enable_cap
                )
                
                print(f"✓ Done")
                print(f"   Original: {text[:60]}{'...' if len(text) > 60 else ''}")
                if formatted != text:
                    print(f"   Formatted: {formatted[:60]}{'...' if len(formatted) > 60 else ''}")
                
                # Output
                self._output_text(formatted)
                print()
            else:
                print("⚠️  No speech detected\n")
        
        except Exception as e:
            print(f"❌ Error: {e}\n")
        
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def _output_text(self, text):
        """Output text according to mode"""
        if self.output_mode in ["clipboard", "both"]:
            pyperclip.copy(text)
        
        if self.output_mode in ["type", "both"]:
            time.sleep(0.05)
            keyboard.write(text)
    
    def run(self):
        """Main loop"""
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=self.audio_callback,
            blocksize=1024
        )
        self.stream.start()
        
        try:
            keyboard.on_press_key(self.hotkey, lambda _: self.start_recording())
            keyboard.on_release_key(self.hotkey, lambda _: self.stop_recording())
            
            print(f"✅ Ready! Hold '{self.hotkey.upper()}' to dictate...\n")
            keyboard.wait("esc")
        
        finally:
            self.stream.stop()
            self.stream.close()
        
        print("\n👋 Goodbye!")


def test_microphone():
    """Test microphone"""
    print("🎤 Testing microphone...")
    print("   Please speak for 3 seconds...")
    
    try:
        recording = sd.rec(int(3 * 16000), samplerate=16000, channels=1, dtype='float32')
        sd.wait()
        
        max_val = np.max(np.abs(recording))
        
        if max_val > 0.01:
            print(f"   ✓ Microphone working! Level: {max_val:.3f}\n")
            return True
        else:
            print("   ⚠️  Microphone level too low\n")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
        return False


def load_or_setup_config():
    """Load existing config or run setup"""
    # Check for existing config
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"✓ Loaded configuration from {CONFIG_FILE}")
            return config
        except:
            pass
    
    # Run setup wizard
    return SetupWizard.run()


def main():
    """Main entry point"""
    try:
        # Load or setup configuration
        config = load_or_setup_config()
        
        # Test microphone
        if not test_microphone():
            print("Please check your microphone settings and try again.")
            input("\nPress Enter to exit...")
            return
        
        # Start dictation
        app = WhisperDictation(config)
        app.run()
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
