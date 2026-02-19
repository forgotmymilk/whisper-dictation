# Whisper Dictation System

> **Personal Daily Driver** — This is the stable, personal-use version for everyday dictation.
> For the commercial product (VoicePro), see [`D:\GAG\projects\voicepro`](file:///D:/GAG/projects/voicepro).

Real-time speech-to-text dictation for Windows with RTX 4070 Ti Super GPU acceleration.

**Location:** `D:\GAG\projects\whisper-dictation`

---

## Quick Start

### 1. Install (First Time Only)
```batch
install.bat
```

### 2. Test Setup
```batch
test-setup.bat
```

### 3. Start Dictating
```batch
start-dictation.bat
```

**Controls:**
- **HOLD F15** (default) → Speak → **RELEASE** to transcribe and auto-type
- **ESC** to exit

---

## X-Mouse Button Control Setup

Since the hotkey is changed from Print Screen to **F15**, you can map any mouse button to trigger it:

### Setup Steps:

1. **Open X-Mouse Button Control**
2. **Select your application profile** (or Global)
3. **Click the mouse button** you want to use
4. **Choose "Simulated Keys"**
5. **Enter:** `{F15}`
6. **Set mode:** "Pressed" (for push-to-talk behavior)
7. **Click OK**

### Alternative Hotkeys:

Edit `config.json`:

```json
{
  "hotkey": "f16",
  "language": null,
  "model": "large-v3",
  "compute_type": "float16"
}
```

**X-Mouse Compatible Keys:**
- `f15`, `f16`, `f17`, `f18`, `f19`, `f20` - Best choice (rarely used)
- `ctrl+shift+d` - Key combination
- `insert`, `pause`, `scroll lock` - Dedicated keys

**Recommended:** Use F15-F20 - these keys exist virtually and won't conflict with any software.

---

## File Structure

```
whisper-dictation/
├── .venv/                      # Virtual environment (created by install.bat)
├── install.bat                 # First-time setup
├── start-dictation.bat        # Launch dictation mode
├── start-transcribe.bat       # Launch file transcription
├── test-setup.bat             # Verify installation
├── dictation.py               # Real-time dictation script
├── transcribe.py              # File transcription script
├── test_setup.py              # Installation tester
├── config.json                # Hotkey and settings
└── requirements.txt           # Python dependencies
```

---

## Portability (Reusable After Reinstall)

This folder is **completely portable**:

### Backup:
Simply copy the entire `whisper-dictation` folder to:
- External drive
- Cloud storage (OneDrive, Dropbox)
- Network drive

### Restore on New System:
1. Copy folder to same location: `D:\GAG\projects\whisper-dictation`
2. Run `install.bat` (recreates virtual environment)
3. Done!

**Note:** Models are downloaded on first run (~3GB) and cached in:
- `%USERPROFILE%\.cache\whisper` (model files)

---

## Configuration

### config.json Options:

```json
{
  "hotkey": "f15",
  "language": null,
  "model": "large-v3",
  "compute_type": "float16"
}
```

| Option | Values | Description |
|--------|--------|-------------|
| `hotkey` | `"f15"`, `"f16"`, `"ctrl+shift+d"`, etc. | Trigger key |
| `language` | `null` (auto), `"zh"` (Chinese), `"en"` (English) | Language |
| `model` | `"tiny"`, `"base"`, `"medium"`, `"large-v3"` | Model size |
| `compute_type` | `"float16"`, `"int8"` | GPU precision |

### Model Performance (RTX 4070 Ti Super):

| Model | Delay | VRAM | Accuracy |
|-------|-------|------|----------|
| tiny | <0.5s | ~1GB | Basic |
| base | ~0.5s | ~1GB | Decent |
| medium | ~1s | ~5GB | Very Good |
| **large-v3** | **1-2s** | **~10GB** | **Excellent** |

**Recommendation:** Use large-v3 for maximum accuracy (ideal for Chinese + English mixed speech).

---

## Language Settings

### Auto-Detect (Default):
```json
"language": null
```

### Force Chinese:
```json
"language": "zh"
```

### Force English:
```json
"language": "en"
```

---

## Troubleshooting

### "Virtual environment not found"
Run `install.bat` first.

### "CUDA not available"
```batch
.venv\Scripts\activate.bat
python -c "import torch; print(torch.cuda.is_available())"
```
If False, reinstall:
```batch
.venv\Scripts\activate.bat
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### "No module named 'faster_whisper'"
Run `install.bat` to install all dependencies.

### Microphone not detected
1. Windows Settings → Privacy → Microphone → Allow apps to access microphone
2. Set your microphone as default recording device

### Hotkey not working
1. Check X-Mouse is sending the correct key
2. Verify config.json has correct hotkey name
3. Try a different hotkey (F16, F17, etc.)

### Low accuracy
1. Check microphone quality (use headset or dedicated mic)
2. Speak clearly and at normal pace
3. Ensure using large-v3 model
4. Try forcing language: `"language": "zh"`

---

## Privacy

✅ **100% Offline**
- No telemetry
- No API calls
- No cloud processing
- Works without internet (after model download)

---

## Performance Tips

### For RTX 4070 Ti Super:
- Use `float16` compute_type (best balance of speed/accuracy)
- Keep model as `large-v3`
- Close other GPU-intensive apps

### For Lower VRAM (if needed):
```json
{
  "model": "large-v3",
  "compute_type": "int8"
}
```
Saves ~40% VRAM with minimal accuracy loss.

---

## Daily Workflow

1. **Start dictation:** Double-click `start-dictation.bat`
2. **Dictate:** Hold your X-Mouse configured button, speak, release
3. **Text appears** in your active window instantly
4. **Exit:** Press ESC or close the window

---

## System Requirements

- Windows 10/11
- NVIDIA GPU (RTX 4070 Ti Super recommended)
- CUDA 12.1+ support
- 12GB+ VRAM for large-v3
- Microphone
- X-Mouse Button Control (optional, for mouse integration)

---

## Updates

To update packages:
```batch
.venv\Scripts\activate.bat
pip install --upgrade faster-whisper torch
```

---

**Status:** Production-ready, portable dictation system
