# Whisper Dictation AGENTS.md

## Project Overview

Whisper Dictation is a real-time speech-to-text desktop application for Windows with GPU acceleration using OpenAI's Whisper model.

**Tech Stack:** Python 3, faster-whisper, PyTorch 2.1+, CUDA, sounddevice, pynput, pyperclip

---

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

### Testing & Diagnostics
```bash
# Verify installation and dependencies
python test_setup.py

# Check microphone configuration
python check-mic.py

# Run system diagnostics
python diagnose.py
```

### Launch Scripts
```bash
# Windows batch files
start-universal.bat    # Universal variant
start-enhanced.bat     # Enhanced variant  
start-simple.bat       # Simple variant
test-microphone.bat    # Microphone test
test-keys.bat          # Hotkey test
run-diagnose.bat       # Full diagnostics
```

### Python Unit Testing (if pytest added)
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_transcription.py

# Run specific test
pytest tests/test_transcription.py::test_basic_transcription

# Run with coverage
pytest --cov=. tests/
```

---

## Code Style Guidelines

### Naming Conventions

**Python:**
- Functions/Variables: snake_case (`get_device_info()`, `transcribe_audio()`)
- Classes: PascalCase (`WhisperDictation`, `DeviceProfiler`)
- Constants: UPPER_SNAKE_CASE (`MAX_AUDIO_DURATION`, `SAMPLE_RATE`)
- Private members: underscore prefix (`_format_text()`, `_detect_device()`)

**File Naming:**
- Python files: snake_case (`dictation-universal.py`, `check_mic.py`)
- Batch files: kebab-case (`start-universal.bat`, `test-microphone.bat`)

### Import Organization
```python
# Order: stdlib → third-party → local imports
import os
import json
import asyncio
import numpy as np
from typing import Optional, Dict, List

from faster_whisper import WhisperModel
import sounddevice as sd
import webrtcvad
from scipy.io.wavfile import write
from pynput import keyboard

from config import Config
from device_profiler import DeviceProfiler
```

### Type Hints
```python
# Required on all function signatures
def transcribe(self, audio_data: np.ndarray) -> str:
    """Transcribe audio to text."""
    pass

def get_device_info(self) -> Optional[Dict[str, any]]:
    """Get current device information."""
    pass
```

### Code Structure Patterns

**Class-based Architecture:**
```python
class WhisperDictation:
    """Main dictation application with real-time speech-to-text."""

    def __init__(self):
        self.config = Config()
        self.device_profiler = DeviceProfiler()
        self.model: Optional[WhisperModel] = None

    def initialize(self) -> bool:
        """Initialize components. Returns True on success."""
        pass

    async def transcribe(self, audio_data: np.ndarray) -> str:
        """Transcribe audio using Whisper model."""
        pass
```

### Error Handling Best Practices

1. **Catch Specific Exceptions:**
```python
try:
    result = await self.model.transcribe(audio_data)
except OSError as e:
    # Device/audio issues
    print(f"Audio device error: {e}")
except Exception as e:
    # Unexpected errors - log and re-raise
    logger.error(f"Transcription failed: {e}")
    raise
```

2. **Provide Fallbacks:**
```python
try:
    device = self.device_profiler.get_best_device()
except RuntimeError as e:
    # Fall back to CPU if GPU unavailable
    print(f"GPU unavailable: {e}, falling back to CPU")
    device = "cpu"
```

3. **User-Friendly Messages:**
```python
except RuntimeError as e:
    print(f"Error: {e}\nFalling back to CPU mode. Install CUDA for better performance.")
```

### Formatting Standards

**String Formatting:**
```python
# Use f-strings
message = f"Detected device: {device_name}"
error_msg = f"Failed to load model {model_name}: {e}"

# Use json.dumps for config files
json.dump(config, file, indent=2, ensure_ascii=False)
```

**File I/O:**
```python
# Always use with statements + UTF-8 encoding
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

with open("output.txt", "w", encoding="utf-8") as f:
    f.write(text)
```

### Documentation Comments
```python
class SmartFormatter:
    """Universal Text Formatter for Chinese & English.
    
    Features:
        - Auto punctuation for both languages
        - Smart capitalization
        - Layout formatting
    """

    @staticmethod
    def format_text(text: str, lang: Optional[str] = None) -> str:
        """Format text with punctuation and capitalization.
        
        Args:
            text: Input text to format
            lang: Language hint ('zh', 'en', 'mixed', or None for auto-detect)
            
        Returns:
            Formatted text string
        """
        pass
```

---

## Configuration

### Core Settings (user-config.json)
```json
{
  "hotkey": "f15",
  "language": null,
  "model": "large-v3",
  "compute_type": "float16",
  "device": "cuda",
  "enable_punctuation": true,
  "enable_formatting": true,
  "output_mode": "both"
}
```

### Output Modes
1. **type**: Types text directly using pynput.keyboard
2. **clipboard**: Copies to clipboard using pyperclip
3. **both**: Types AND copies to clipboard

---

## Architecture

```
WhisperDictation
├── DeviceProfiler    # GPU/CPU detection
├── SmartFormatter    # Text processing
├── Recording Pipeline
│   ├── Audio Capture (sounddevice)
│   ├── VAD (webrtcvad)
│   └── Whisper Inference (faster-whisper)
└── Output (keyboard/pyperclip)
```

---

## Key Dependencies

- **faster-whisper:** Optimized Whisper model
- **PyTorch 2.1+:** GPU acceleration
- **sounddevice:** Audio capture
- **pynput:** Keyboard simulation
- **pyperclip:** Clipboard operations
- **numpy:** Audio processing

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Microphone not detected | Run `python check-mic.py` |
| GPU not found | Run `python diagnose.py` |
| Hotkey not working | Run `test-keys.bat` |
| Model download failed | Check internet, verify CUDA |

---

## Development Workflow

1. Modify code → Test with batch files
2. Run diagnostics → Verify settings
3. Update docs → Keep AGENTS.md current
