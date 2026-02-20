#!/usr/bin/env python3
"""
Enhanced Whisper Dictation with Smart Formatting

Features:
- Chinese/English mixed input support
- Auto punctuation for Chinese text
- Smart text formatting and layout

Usage:
    python dictation-enhanced.py
"""

import sounddevice as sd
import numpy as np
import keyboard
import pyperclip
import time
import threading
import json
import os
import re
from faster_whisper import WhisperModel
from scipy.io.wavfile import write as wav_write
import tempfile

# ============ CONFIGURATION ============
DEFAULT_HOTKEY = "f15"
CONFIG_FILE = "config.json"

# 中文标点符号映射规则
PUNCTUATION_RULES = {
    # 语气词后添加标点
    'particles': {
        '啊': '！', '呀': '！', '哇': '！', '啦': '！', '呢': '？', '吧': '？',
        '吗': '？', '么': '？', '嘛': '！', '哦': '。', '诶': '，',
    },
    # 句首词提示
    'sentence_starters': ['首先', '其次', '然后', '接着', '最后', '总之', '所以', '因此', '但是', '然而', '不过'],
    # 连接词
    'connectors': ['而且', '并且', '或者', '还是', '因为', '由于', '虽然', '尽管'],
}
# ======================================

class SmartFormatter:
    """智能文本格式化器"""
    
    @staticmethod
    def add_punctuation(text: str) -> str:
        """为中文文本添加标点符号"""
        if not text or not SmartFormatter.contains_chinese(text):
            return text
        
        # 如果已经有足够的标点，不再添加
        if SmartFormatter.has_sufficient_punctuation(text):
            return text
        
        result = text
        
        # 1. 在语气词后添加标点
        for particle, punct in PUNCTUATION_RULES['particles'].items():
            pattern = f'{particle}(?![，。？！,\.?!])'
            result = re.sub(pattern, f'{particle}{punct}', result)
        
        # 2. 在句首词前添加句号或换行（如果前面没有标点）
        for starter in PUNCTUATION_RULES['sentence_starters']:
            pattern = f'(?<![，。？！,\.?!\n]){starter}'
            result = re.sub(pattern, f'。{starter}', result)
        
        # 3. 在连接词前添加逗号（如果前面没有标点）
        for connector in PUNCTUATION_RULES['connectors']:
            pattern = f'(?<![，。？！,\.?!\n]){connector}'
            result = re.sub(pattern, f'，{connector}', result)
        
        # 4. 长句智能切分（超过25字且无标点的句子）
        result = SmartFormatter.split_long_sentences(result)
        
        # 5. 清理重复的标点
        result = SmartFormatter.clean_duplicate_punctuation(result)
        
        # 6. 句尾添加句号（如果没有标点）
        if result and not result[-1] in '，。？！,\.?!':
            result += '。'
        
        return result
    
    @staticmethod
    def contains_chinese(text: str) -> bool:
        """检查文本是否包含中文"""
        return bool(re.search(r'[\u4e00-\u9fff]', text))
    
    @staticmethod
    def has_sufficient_punctuation(text: str) -> bool:
        """检查文本是否已有足够的标点符号"""
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        punctuations = len(re.findall(r'[，。？！]', text))
        # 如果每10个汉字至少有1个标点，认为标点充足
        return chinese_chars > 0 and punctuations >= chinese_chars / 15
    
    @staticmethod
    def split_long_sentences(text: str, max_length: int = 25) -> str:
        """将长句按语义切分"""
        # 先按已有标点分割
        segments = re.split(r'([，。？！])', text)
        result = []
        
        for i, segment in enumerate(segments):
            if not segment or segment in '，。？！':
                result.append(segment)
                continue
            
            # 检查这个片段的长度
            chinese_chars = re.findall(r'[\u4e00-\u9fff]', segment)
            if len(chinese_chars) > max_length:
                # 尝试在自然停顿处切分
                segment = SmartFormatter.insert_breaks(segment, max_length)
            
            result.append(segment)
        
        return ''.join(result)
    
    @staticmethod
    def insert_breaks(text: str, max_length: int = 25) -> str:
        """在长文本中插入切分点"""
        # 切分标记词
        break_points = ['的', '了', '是', '在', '和', '与', '对', '为', '有']
        
        result = []
        current = ""
        char_count = 0
        
        for char in text:
            current += char
            if re.match(r'[\u4e00-\u9fff]', char):
                char_count += 1
            
            # 如果达到长度限制且在切分点
            if char_count >= max_length and char in break_points:
                result.append(current + '，')
                current = ""
                char_count = 0
        
        if current:
            result.append(current)
        
        return ''.join(result)
    
    @staticmethod
    def clean_duplicate_punctuation(text: str) -> str:
        """清理重复的标点符号"""
        # 多个相同标点合并
        text = re.sub(r'[，,]{2,}', '，', text)
        text = re.sub(r'[。.]{2,}', '。', text)
        text = re.sub(r'[！!]{2,}', '！', text)
        text = re.sub(r'[？?]{2,}', '？', text)
        
        # 连续的逗号句号等整理
        text = re.sub(r'，。', '。', text)
        text = re.sub(r'。，', '。', text)
        text = re.sub(r'，？', '？', text)
        text = re.sub(r'？，', '？', text)
        
        return text
    
    @staticmethod
    def format_layout(text: str) -> str:
        """智能排版格式化"""
        if not text:
            return text
        
        # 1. 优化中英文间距
        text = SmartFormatter.optimize_spacing(text)
        
        # 2. 段落智能分段
        text = SmartFormatter.paragraph_segmentation(text)
        
        # 3. 清理多余空格
        text = re.sub(r'  +', ' ', text)
        
        # 4. 标点符号后添加适当空格（中英文混排时）
        text = SmartFormatter.punctuation_spacing(text)
        
        return text.strip()
    
    @staticmethod
    def optimize_spacing(text: str) -> str:
        """优化中英文之间的间距"""
        # 在中文字符和英文/数字之间添加空格
        # 中文后接英文/数字
        text = re.sub(r'([\u4e00-\u9fff])([a-zA-Z0-9])', r'\1 \2', text)
        # 英文/数字后接中文
        text = re.sub(r'([a-zA-Z0-9])([\u4e00-\u9fff])', r'\1 \2', text)
        
        # 清理多余空格
        text = re.sub(r'  +', ' ', text)
        
        return text
    
    @staticmethod
    def paragraph_segmentation(text: str) -> str:
        """根据语义进行段落分段"""
        # 识别段落标记词
        para_markers = ['首先', '其次', '第一', '第二', '第三', '最后', '总结', '总之', '综上']
        
        for marker in para_markers:
            # 在段落标记词前添加换行（如果不是在开头）
            pattern = f'(?<!^)(?<![\n]){marker}'
            text = re.sub(pattern, f'\n{marker}', text)
        
        # 处理过长的段落（超过80字且没有换行）
        lines = text.split('\n')
        result_lines = []
        
        for line in lines:
            if len(line) > 80 and SmartFormatter.contains_chinese(line):
                line = SmartFormatter.break_long_paragraph(line)
            result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    @staticmethod
    def break_long_paragraph(text: str) -> str:
        """将长段落按语义切分成多行"""
        # 按句号切分，然后每2-3句换行
        sentences = re.split(r'([。！？])', text)
        
        result = []
        current_line = ""
        sentence_count = 0
        
        for i in range(0, len(sentences), 2):
            if i < len(sentences):
                sentence = sentences[i]
                if i + 1 < len(sentences):
                    sentence += sentences[i + 1]  # 加上标点
                
                current_line += sentence
                sentence_count += 1
                
                # 每2-3个句子换行
                if sentence_count >= 2:
                    result.append(current_line)
                    current_line = ""
                    sentence_count = 0
        
        if current_line:
            result.append(current_line)
        
        return '\n'.join(result)
    
    @staticmethod
    def punctuation_spacing(text: str) -> str:
        """处理标点符号后的间距"""
        # 在中文标点后的英文前添加空格
        text = re.sub(r'([。！？，；：])([a-zA-Z])', r'\1 \2', text)
        
        # 在英文后的中文标点前移除空格
        text = re.sub(r'([a-zA-Z]) ([。！？，；：])', r'\1\2', text)
        
        return text
    
    @staticmethod
    def process(text: str, add_punct: bool = True, format_layout: bool = True) -> str:
        """完整的文本处理流程"""
        if not text:
            return text
        
        original_text = text.strip()
        
        # 步骤1: 添加标点符号
        if add_punct and SmartFormatter.contains_chinese(original_text):
            text = SmartFormatter.add_punctuation(text)
        
        # 步骤2: 格式化排版
        if format_layout:
            text = SmartFormatter.format_layout(text)
        
        return text


class WhisperDictation:
    def __init__(self):
        self.is_recording = False
        self.audio_buffer = []
        self.sample_rate = 16000
        self.stream = None
        self.formatter = SmartFormatter()
        
        # Load or create config
        self.config = self.load_config()
        self.hotkey = self.config.get("hotkey", DEFAULT_HOTKEY)
        self.language = self.config.get("language", None)  # None = auto-detect
        self.model_size = self.config.get("model", "large-v3")
        self.compute_type = self.config.get("compute_type", "float16")
        self.enable_punctuation = self.config.get("enable_punctuation", True)
        self.enable_formatting = self.config.get("enable_formatting", True)
        self.initial_prompt = self.config.get("initial_prompt", None)
        
        print("=" * 60)
        print("Enhanced Whisper Dictation System")
        print("=" * 60)
        print(f"\nConfiguration:")
        print(f"  Hotkey: {self.hotkey.upper()}")
        print(f"  Model: {self.model_size}")
        print(f"  Language: {self.language or 'Auto-detect'}")
        print(f"  Compute: {self.compute_type}")
        print(f"  Auto Punctuation: {'Yes' if self.enable_punctuation else 'No'}")
        print(f"  Smart Formatting: {'Yes' if self.enable_formatting else 'No'}")
        
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
            "compute_type": self.compute_type,
            "enable_punctuation": self.enable_punctuation,
            "enable_formatting": self.enable_formatting,
            "initial_prompt": self.initial_prompt
        }
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
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
            
            # Transcribe with optimized parameters for mixed language
            transcribe_options = {
                "beam_size": 5,
                "best_of": 5,
                "condition_on_previous_text": True,
                "language": self.language,
                "vad_filter": True,  # 启用语音活动检测
                "vad_parameters": {
                    "min_silence_duration_ms": 300,
                    "max_speech_duration_s": duration + 1
                }
            }
            
            # 添加初始提示以改善中文标点
            if self.initial_prompt:
                transcribe_options["initial_prompt"] = self.initial_prompt
            
            segments, info = self.model.transcribe(temp_path, **transcribe_options)
            
            # Combine all segments
            text = " ".join([segment.text.strip() for segment in segments])
            
            if text:
                # 应用智能格式化
                original_text = text
                formatted_text = self.formatter.process(
                    text, 
                    add_punct=self.enable_punctuation,
                    format_layout=self.enable_formatting
                )
                
                print(f"✓ Raw: {original_text}")
                if formatted_text != original_text:
                    print(f"✓ Formatted: {formatted_text}")
                
                # Copy to clipboard
                pyperclip.copy(formatted_text)
                
                # Auto-type into active window
                time.sleep(0.05)
                keyboard.write(formatted_text)
                
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
