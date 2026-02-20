# Universal Whisper Dictation 🎤

A portable, user-friendly voice dictation system with smart formatting for Chinese, English, and mixed-language input.

## 🌟 Features

### Multi-Language Support
- **Chinese**: Auto punctuation (，。！？), smart paragraph breaks
- **English**: Auto punctuation, smart capitalization, sentence breaks
- **Mixed**: Optimized spacing between Chinese and English

### Smart Formatting
- **Auto Punctuation**: Adds appropriate punctuation based on context
- **Smart Capitalization**: Capitalizes first word of sentences and proper nouns
- **Layout Optimization**: Breaks long text into readable paragraphs
- **Language Spacing**: Adds proper spacing between Chinese and English

### Universal Compatibility
- **Auto Detection**: Automatically detects GPU/CPU capability
- **Flexible Hardware**: Works on high-end GPUs to integrated graphics
- **Portable**: No admin rights required, runs from any folder
- **Cross-Device**: Easy migration between computers

### User-Friendly
- **Setup Wizard**: Interactive configuration for non-technical users
- **Visual Feedback**: Clear indicators for recording/processing
- **Customizable**: Profile-based settings for different users

## 🚀 Quick Start

### First Time Setup

1. **Download** the project folder
2. **Double-click** `portable-setup.bat`
3. **Wait** for installation (5-10 minutes)
4. **Double-click** `start-universal.bat`
5. **Follow** the interactive setup wizard
6. **Start** dictating!

### Daily Use

Simply double-click `start-universal.bat` and:
- **HOLD** your configured hotkey (default: F15)
- **SPEAK** naturally in Chinese, English, or mixed
- **RELEASE** to transcribe and auto-type
- Press **ESC** to exit

## ⚙️ Configuration

### Setup Wizard (Recommended)

The setup wizard runs automatically on first launch:
- **Language preference**: Chinese/English/Mixed
- **Text style**: Casual/Formal/Business
- **Hotkey configuration**: Customize your trigger key
- **Feature toggles**: Enable/disable punctuation, formatting

### Manual Configuration

Edit `user-config.json`:

```json
{
  "hotkey": "f15",
  "language": null,
  "model": "auto",
  "compute_type": "auto",
  "device": "auto",
  "enable_punctuation": true,
  "enable_formatting": true,
  "enable_capitalization": true,
  "output_mode": "type"
}
```

### Configuration Options

| Option | Values | Description |
|--------|--------|-------------|
| `hotkey` | `"f15"`, `"ctrl+shift+d"`, etc. | Trigger key |
| `language` | `null`, `"zh"`, `"en"` | Language (null=auto) |
| `model` | `"auto"`, `"tiny"` to `"large-v3"` | Whisper model size |
| `device` | `"auto"`, `"cuda"`, `"cpu"` | Processing device |
| `enable_punctuation` | `true`, `false` | Auto-add punctuation |
| `enable_formatting` | `true`, `false` | Smart layout formatting |
| `enable_capitalization` | `true`, `false` | Auto-capitalize English |
| `output_mode` | `"type"`, `"clipboard"`, `"both"` | Output destination |

## 📝 Formatting Examples

### Chinese Input
```
Input:  今天天气真好啊我要去公园玩然后回家吃饭
Output: 今天天气真好啊！我要去公园玩，然后回家吃饭。
```

### English Input
```
Input:  hello today is a great day i want to go to the park
Output: Hello. Today is a great day. I want to go to the park.
```

### Mixed Input
```
Input:  我有5个apple和3个banana today is great
Output: 我有 5 个 apple 和 3 个 banana. Today is great.
```

### Long Text
```
Input:  首先我们要准备工作然后检查设备最后开始录音
Output: 首先，我们要准备工作。
       然后，检查设备。
       最后，开始录音。
```

## 🖱️ Mouse Integration (X-Mouse Button Control)

Map any mouse button to your hotkey:

1. Download and install [X-Mouse Button Control](https://www.highrez.co.uk/downloads/xmousebuttoncontrol.htm)
2. Open X-Mouse and select your mouse
3. Click the button you want to use
4. Select "Simulated Keys"
5. Enter: `{F15}` (or your configured hotkey)
6. Set mode to "Pressed"
7. Click OK

**Recommended hotkeys for mouse:** F15, F16, F17, F18, F19, F20 (virtual keys, no conflicts)

## 💾 Portability

### Backup
Simply copy the entire folder to:
- External drive
- Cloud storage (OneDrive, Dropbox)
- USB stick

### Restore on New Computer
1. Copy folder to new computer
2. Delete `device-profile.json` (forces re-detection)
3. Run `start-universal.bat`
4. The setup wizard will reconfigure for new hardware

### Files to Keep
- `user-config.json` - Your personal settings
- `dictation-universal.py` - Main program
- `.venv/` folder - Python environment

### Files Safe to Delete
- `device-profile.json` - Auto-regenerated
- Model cache in `%USERPROFILE%\.cache\whisper`

## 🖥️ System Requirements

### Minimum (CPU Mode)
- Windows 10/11
- 4GB RAM
- Microphone
- Python 3.8+

### Recommended (GPU Mode)
- Windows 10/11
- NVIDIA GPU with 2GB+ VRAM
- 8GB RAM
- Microphone
- CUDA-capable GPU

### Optimal (High Performance)
- Windows 10/11
- RTX 3060 or better (6GB+ VRAM)
- 16GB RAM
- Quality microphone
- SSD storage

## 🔧 Troubleshooting

### "Virtual environment not found"
Run `portable-setup.bat` first

### "CUDA not available"
The system automatically falls back to CPU mode. For GPU support:
```batch
.venv\Scripts\activate.bat
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### "Microphone not detected"
1. Windows Settings → Privacy → Microphone
2. Enable "Allow apps to access microphone"
3. Set your microphone as default recording device

### "Hotkey not working"
1. Try a different hotkey in config
2. Run as administrator (if keyboard library fails)
3. Check if antivirus is blocking keyboard hooks

### "Low accuracy"
1. Use a better microphone (headset recommended)
2. Speak clearly and at normal pace
3. Switch to larger model in config
4. Check microphone input levels

### "Slow performance"
1. Use a smaller model (medium → small → base)
2. Switch to int8 compute type
3. Close other GPU-intensive applications
4. Consider CPU mode for non-RTX GPUs

## 🎯 Tips for Best Results

### Chinese Input
- Speak naturally, system handles punctuation
- Use "首先、其次、然后" for automatic paragraph breaks
- System adds appropriate spacing around English words

### English Input
- The system capitalizes sentence starts
- "I" is automatically capitalized
- Proper nouns may need manual correction

### Mixed Input
- Seamlessly switch between languages
- System optimizes spacing automatically
- Best with large-v3 model

### Performance Optimization
- **Fastest**: tiny model, CPU, no formatting
- **Balanced**: base/small model, GPU, basic formatting
- **Best Quality**: large-v3 model, GPU, full formatting

## 📁 File Structure

```
whisper-dictation/
├── dictation-universal.py      # Main program
├── start-universal.bat         # Launch script
├── portable-setup.bat          # Installation
├── user-config.json            # User settings (auto-created)
├── device-profile.json         # Device info (auto-created)
├── .venv/                      # Python environment
└── README.md                   # This file
```

## 🔒 Privacy & Security

✅ **100% Offline**
- No cloud processing
- No telemetry
- No API calls
- Models downloaded once, cached locally

✅ **Portable**
- No system installation
- No registry changes
- No admin rights needed
- Easy complete removal

## 🆘 Getting Help

1. Check the troubleshooting section above
2. Review the configuration options
3. Try resetting config (delete user-config.json)
4. Re-run portable-setup.bat

## 📝 Version History

### v2.0 - Universal Edition
- Added English formatting support
- Portable configuration system
- Device auto-detection
- Setup wizard for non-technical users
- Mixed-language optimization
- Smart layout formatting

### v1.0 - Original
- Basic Chinese dictation
- GPU acceleration
- Configurable hotkeys

## 📄 License

This project uses:
- [OpenAI Whisper](https://github.com/openai/whisper) - MIT License
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) - MIT License

---

**Made with ❤️ for effortless voice typing**
