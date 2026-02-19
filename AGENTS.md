# Whisper Dictation AGENTS.md

## Project Overview

Whisper Dictation is a real-time speech-to-text desktop application for Windows with GPU acceleration. It uses OpenAI's Whisper model with faster-whisper for optimized inference.

**Tech Stack:** Python 3, faster-whisper, PyTorch 2.1+, CUDA 12.1, sounddevice, pyaudio, webrtcvad

## Build, Test & Development Commands

### Virtual Environment
```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS
```

### Running the Application
```bash
# Universal variant (recommended)
python dictation-universal.py

# Enhanced variant (Chinese punctuation focused)
python dictation-enhanced.py

# Simple variant
python dictation-simple.py
```

### Testing & Debugging
```bash
# Check microphone and system setup
python check-mic.py

# Run system diagnostics
python diagnose.py

# Test setup
python test-setup.py
```

### Launch Scripts
```bash
# Run specific variant via batch file
start-universal.bat  # Universal variant
start-enhanced.bat   # Enhanced variant
start-simple.bat     # Simple variant
```

### Manual Testing Commands
```bash
# Check microphone configuration
test-microphone.bat

# Verify hotkey functionality
test-keys.bat

# Run all diagnostics
run-diagnose.bat
```

## Code Style Guidelines

### General Principles
- **Modular Design:** Keep functionality separated into classes and functions
- **Configuration-Driven:** Use JSON files for settings (config.json)
- **Error Handling:** Use try/catch with graceful degradation
- **Device-Aware:** Always check for GPU availability and fall back to CPU
- **User-Friendly:** Provide clear error messages and fallback options

### Naming Conventions

**Python:**
- **Functions/Variables:** snake_case (`get_device_info()`, `transcribe_audio()`)
- **Classes:** PascalCase (`WhisperDictation`, `DeviceProfiler`)
- **Constants:** UPPER_SNAKE_CASE (`MAX_AUDIO_DURATION`, `MODEL_TYPES`)
- **Private members:** underscore prefix (`_format_text()`, `_detect_device()`)

**File Naming:**
- Python files: snake_case (`dictation-universal.py`, `check-mic.py`)
- Batch files: kebab-case or snake_case (`start-universal.bat`, `test-microphone.bat`)

### Import Organization
```python
# Order: stdlib → third-party → local imports
import os
import json
import asyncio
import numpy as np

from faster_whisper import WhisperModel
import sounddevice as sd
import webrtcvad
from scipy.io.wavfile import write
from pynput import keyboard

from config import Config
from device_profiler import DeviceProfiler
```

### Code Structure Patterns

**Class-based Architecture:**
```python
class WhisperDictation:
    def __init__(self):
        self.config = Config()
        self.device_profiler = DeviceProfiler()
        self.model = None

    def initialize(self):
        # Initialize components
        pass

    async def start_recording(self):
        # Recording logic
        pass

    async def transcribe(self, audio_data):
        # Transcription logic
        pass
```

**Configuration-Driven Design:**
```python
class Config:
    def __init__(self):
        self.load_config()

    def load_config(self):
        # Load from config.json with fallbacks
        pass
```

**Error Handling Pattern:**
```python
try:
    result = await self.whisper_model.transcribe(audio_data)
except Exception as e:
    logger.error(f"Transcription failed: {e}")
    # Fall back to CPU or retry
    result = await self._transcribe_with_cpu(audio_data)
```

### Formatting Standards

**String Formatting:**
```python
# Use f-strings for simple formatting
message = f"Detected device: {device_name}"
error_msg = f"Failed to load model {model_name}: {str(e)}"

# Use json.dumps for config files
json.dump(config, file, indent=2, ensure_ascii=False)
```

**File I/O:**
```python
# Always use with statements for file operations
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# Use UTF-8 encoding for cross-platform compatibility
with open("output.txt", "w", encoding="utf-8") as f:
    f.write(text)
```

### Async Programming
```python
# Use async/await for I/O operations
async def record_audio(duration=3):
    audio = sd.rec(int(duration * SAMPLE_RATE), 
                   samplerate=SAMPLE_RATE, 
                   channels=1)
    await asyncio.sleep(duration)
    return audio

# Handle concurrent operations
async def run_dictation():
    while True:
        audio = await record_audio()
        text = await transcribe(audio)
        await type_text(text)
```

### Error Handling Best Practices

1. **Catch Specific Exceptions:**
```python
try:
    result = await self.model.transcribe(audio)
except OSError as e:
    # Device/audio issues
    logger.error(f"Audio device error: {e}")
except Exception as e:
    # Unexpected errors
    logger.error(f"Transcription error: {e}")
    raise
```

2. **Provide Fallbacks:**
```python
try:
    device = self.device_profiler.get_best_device()
except RuntimeError as e:
    # Fall back to CPU if GPU unavailable
    logger.warning(f"GPU unavailable: {e}")
    device = "cpu"
```

3. **User-Friendly Messages:**
```python
except RuntimeError as e:
    print(f"Error: {e}\nFalling back to CPU mode. Install CUDA for better performance.")
```

### Documentation Comments

```python
class WhisperDictation:
    """Main dictation application with real-time speech-to-text.

    Features:
        - GPU-accelerated transcription
        - Smart punctuation and formatting
        - Multi-language support
    """

    async def transcribe(self, audio_data: np.ndarray) -> str:
        """Transcribe audio using Whisper model.

        Args:
            audio_data: numpy array of audio samples

        Returns:
            Transcribed text string
        """
        pass
```

## Test Strategy

### Manual Testing
```bash
# Test microphone input
test-microphone.bat

# Test hotkey registration
test-keys.bat

# Run all diagnostics
run-diagnose.bat
```

### Code Testing (Future)
```bash
# Install pytest if testing framework is added
pip install pytest

# Run all tests
pytest tests/

# Run specific test
pytest tests/test_transcription.py::test_basic_transcription

# Run with coverage
pytest --cov=. tests/
```

## Configuration

### Core Settings (config.json)
```json
{
  "hotkey": "f15",
  "language": null,
  "model": "large-v3",
  "compute_type": "float16",
  "enable_punctuation": true,
  "enable_formatting": false,
  "initial_prompt": "Chinese and English mixed text"
}
```

### Device Detection
- Automatic GPU/CPU switching based on VRAM
- Uses `device-profile.json` for system profiling
- Falls back to CPU if GPU fails

### Output Modes
1. **Type directly:** Uses pynput.keyboard
2. **Clipboard only:** Uses pyperclip
3. **Both:** Simultaneous typing and clipboard

## Architecture Overview

```
WhisperDictation
├── DeviceProfiler (hardware detection)
├── SmartFormatter (text processing)
├── SetupWizard (configuration)
└── Recording Pipeline
    ├── Audio Capture (sounddevice)
    ├── VAD (webrtcvad)
    ├── Whisper Inference (faster-whisper)
    ├── Formatting & Capitalization
    └── Output (keyboard/pyperclip)
```

## Key Dependencies

- **faster-whisper:** Optimized Whisper model wrapper
- **PyTorch 2.1+:** GPU acceleration
- **CUDA 12.1:** NVIDIA GPU support
- **sounddevice:** Audio capture
- **webrtcvad:** Voice Activity Detection
- **pynput:** Keyboard simulation
- **pyperclip:** Clipboard operations
- **numpy:** Audio processing

## Special Considerations

### GPU Optimization
- Use `float16` compute type for NVIDIA GPUs
- Auto-detect VRAM and select appropriate model
- Fall back to CPU gracefully on failures

### Chinese/English Mixed Text
- Use `enable_punctuation: true` for auto-punctuation
- Set `initial_prompt` to describe language mix
- Use `dictation-enhanced.py` variant for Chinese punctuation

### Performance
- Model size: large-v3 (~3GB)
- Initial load time: 10-30 seconds
- Real-time transcription: GPU dependent
- Battery usage: Low with GPU off

### Portability
- All configuration in JSON files
- Virtual environment for dependency isolation
- No build tools required (pure Python)
- Works offline after initial model download

## Common Issues & Solutions

### Microphone Issues
```bash
python check-mic.py
# Or run: test-microphone.bat
```

### GPU Not Detected
```bash
python diagnose.py
# Or run: run-diagnose.bat
```

### Hotkey Conflicts
```bash
python test-keys.bat
# Check for conflicting key bindings
```

### Model Download Failed
- Manual download from HuggingFace
- Place in `.cache/huggingface/hub/`
- Check internet connection
- Verify CUDA installation

## Development Workflow

1. **Modify code** → Update relevant function/class
2. **Test changes** → Run relevant batch test file
3. **Check config** → Verify settings in config.json
4. **Run diagnostics** → Use diagnose.py for issues
5. **Update docs** → Keep README and guides current

## Environment Variables

```bash
# CUDA version
CUDA_VERSION=12.1

# Model cache location
HF_HOME=~/.cache/huggingface

# Audio device
PYAUDIO_DEVICE_INDEX=1
```

## Security Notes

- All operations run locally (no cloud processing)
- API keys not required
- Local file system only
- No network calls except initial model download

## Performance Optimization Tips

1. **Use GPU:** CUDA enabled for best performance
2. **Compute Type:** Use `float16` for RTX series
3. **Model Size:** Balance accuracy vs speed
4. **Audio Quality:** Use good microphone
5. **Background Noise:** Use headphones for dictation
