# Whisper Dictation - Complete Configuration Guide

## Location: `D:\GAG\projects\whisper-dictation\config.json`

---

## 1. BASIC SETTINGS

### `hotkey` - Trigger Key
```json
"hotkey": "f15"
```
**Options:**
- `"f15"` - Recommended for X-Mouse (rarely conflicts)
- `"f16"`, `"f17"`, `"f18"`, `"f19"`, `"f20"` - Alternative F-keys
- `"ctrl+shift+d"` - Key combination
- `"insert"`, `"pause"`, `"scroll lock"` - Dedicated keys
- `"caps lock"` (not recommended - toggles state)

**X-Mouse Setup:**
1. Open X-Mouse Button Control
2. Select mouse button
3. Simulated Keys: `{F15}`
4. Mode: **Pressed** (not "Pressed and released")

---

### `language` - Speech Language
```json
"language": null
```
**Options:**
- `null` - **Auto-detect** (recommended for mixed Chinese/English)
- `"zh"` - **Chinese** (optimized for Mandarin)
- `"en"` - **English**
- `"ja"` - Japanese
- `"ko"` - Korean
- `"fr"` - French
- `"de"` - German
- `"es"` - Spanish

**Recommendation:**
- Use `null` for mixed language speech
- Use `"zh"` if only speaking Chinese
- Use `"en"` if only speaking English

**Full list:** https://github.com/openai/whisper/blob/main/whisper/tokenizer.py

---

### `model` - AI Model Size
```json
"model": "large-v3"
```
**Options:**

| Model | Speed | VRAM | Accuracy | Best For |
|-------|-------|------|----------|----------|
| `"tiny"` | ~0.2s | 1GB | Basic | Testing only |
| `"base"` | ~0.5s | 1GB | Good | Fast transcription |
| `"small"` | ~0.8s | 2GB | Better | Balance |
| `"medium"` | ~1.0s | 5GB | Very Good | Most use cases |
| `"large-v3"` | ~2.0s | 10GB | **Excellent** | **Maximum accuracy** |

**Recommendation for RTX 4070 Ti Super:**
- Use `"large-v3"` for best Chinese + English accuracy
- Use `"medium"` if you want faster response (1s delay)
- GPU has 16GB VRAM, so large-v3 fits comfortably

**Model download:**
- First run downloads ~3GB (large-v3)
- Cached at: `%USERPROFILE%\.cache\whisper`
- Fully offline after first download

---

### `compute_type` - GPU Precision
```json
"compute_type": "float16"
```
**Options:**
- `"float16"` - **Best balance** (recommended for RTX 4070 Ti Super)
- `"int8"` - Lower VRAM, slightly less accurate
- `"float32"` - Maximum accuracy, 2x VRAM usage

**Recommendation:**
- RTX 4070 Ti Super: Use `float16`
- If VRAM issues: Use `int8`

---

## 2. AUDIO QUALITY SETTINGS

### `microphone_gain` - Volume Boost
```json
"microphone_gain": 2.0
```
**Range:** 0.5 - 5.0
**Default:** 1.0 (no change)

**Use when:**
- Microphone is quiet
- Transcription misses words
- Background noise is low

**Example:**
- `"microphone_gain": 1.5` - Boost volume by 50%
- `"microphone_gain": 2.0` - Double volume
- `"microphone_gain": 0.8` - Reduce volume (if too loud)

---

### `noise_threshold` - Silence Detection
```json
"noise_threshold": 0.01
```
**Range:** 0.001 - 0.1
**Default:** 0.01

**What it does:**
- Audio below this level is considered "silence"
- Filters out background noise
- Prevents transcribing room noise

**Adjust when:**
- **Too low (0.001):** Captures background noise
- **Too high (0.05):** Cuts off quiet speech
- **Just right:** Only captures your voice

**Fine-tuning:**
1. Run `test-microphone.bat`
2. Note your speaking volume
3. Set threshold to ~10% of speaking volume

---

### `vad_filter` - Voice Activity Detection
```json
"vad_filter": true
```
**Options:** `true` or `false`

**What it does:**
- Automatically detects when you start/stop speaking
- Removes silence at beginning/end
- Better for long dictations

**Recommendation:**
- `true` - Most cases (especially long speech)
- `false` - If you're cutting off at the end

---

### `vad_parameters` - VAD Fine-tuning
```json
"vad_parameters": {
  "threshold": 0.5,
  "min_speech_duration_ms": 250,
  "max_speech_duration_s": 30
}
```

**`threshold`** (0-1):
- Higher = stricter (only clear speech)
- Lower = more sensitive (catches whispers)

**`min_speech_duration_ms`**:
- Minimum speech to transcribe
- Default: 250ms (quarter second)
- Lower if you speak quickly

**`max_speech_duration_s`**:
- Maximum recording length
- Default: 30 seconds
- Increase for long dictations

---

## 3. TEXT FORMATTING (ADVANCED)

### `auto_punctuation` - Add Punctuation
```json
"auto_punctuation": true
```
**Options:** `true` or `false`

**What it does:**
- Large-v3 model already has good punctuation
- Set to `false` if you want raw output
- Set to `true` to ensure periods/commas

---

### `auto_format` - Format Long Text
```json
"auto_format": true
```
**Options:** `true` or `false`

**What it does:**
- Uses GPT to format long dictations
- Adds paragraphs, fixes grammar
- Makes text reader-friendly

**Example:**
```
Raw: "so i was thinking about the project and we need to finish it by friday but also we need to make sure that the client is happy with the results and i think we should schedule a meeting tomorrow morning at 9am to discuss the timeline and deliverables"

Formatted: "I was thinking about the project. We need to finish it by Friday, but we also need to make sure the client is happy with the results. I think we should schedule a meeting tomorrow morning at 9 AM to discuss the timeline and deliverables."
```

**Note:** Requires internet connection (calls GPT API)

---

### `format_style` - Formatting Style
```json
"format_style": "natural"
```
**Options:**
- `"natural"` - Conversational, friendly
- `"formal"` - Professional, business
- `"concise"` - Short, bullet points
- `"email"` - Email format with greeting/sign-off
- `"markdown"` - Markdown headers and lists

---

### `format_prompt` - Custom Formatting
```json
"format_prompt": "Format this speech into clear paragraphs with proper grammar"
```

**Customize to your needs:**
```json
// For meeting notes
"format_prompt": "Convert this speech into structured meeting notes with action items and decisions"

// For emails
"format_prompt": "Format this as a professional email with subject line, greeting, and sign-off"

// For documentation
"format_prompt": "Format this as technical documentation with clear steps and examples"

// For casual writing
"format_prompt": "Make this sound natural and conversational, fix grammar but keep the tone casual"
```

---

## 4. PERFORMANCE SETTINGS

### `beam_size` - Search Width
```json
"beam_size": 5
```
**Range:** 1 - 10
**Default:** 5

**What it does:**
- Higher = better accuracy, slower
- Lower = faster, less accurate

**Recommendation:**
- `5` - Good balance
- `1` - Fastest (lower quality)
- `10` - Maximum quality (slowest)

---

### `best_of` - Candidate Selection
```json
"best_of": 5
```
**Range:** 1 - 10
**Default:** 5

**What it does:**
- Number of transcription candidates
- Higher = better accuracy
- Lower = faster

**Recommendation:** Keep same as `beam_size`

---

### `condition_on_previous_text` - Context Memory
```json
"condition_on_previous_text": true
```
**Options:** `true` or `false`

**What it does:**
- Uses previous transcription for context
- Better for continuous dictation
- Helps with proper nouns and context

**Recommendation:** `true` for continuous use

---

### `min_duration` - Minimum Recording
```json
"min_duration": 0.5
```
**Range:** 0.1 - 2.0 seconds
**Default:** 0.5

**What it does:**
- Rejects recordings shorter than this
- Prevents accidental key presses
- Filters out coughs/clearing throat

**Adjust when:**
- **Too short:** Accidental triggers
- **Too long:** Misses quick notes

---

## 5. COMPLETE CONFIG EXAMPLES

### Example 1: Maximum Accuracy (Chinese + English)
```json
{
  "hotkey": "f15",
  "language": null,
  "model": "large-v3",
  "compute_type": "float16",
  "microphone_gain": 1.5,
  "beam_size": 5,
  "best_of": 5,
  "vad_filter": true
}
```

### Example 2: Fast Response (English only)
```json
{
  "hotkey": "f15",
  "language": "en",
  "model": "medium",
  "compute_type": "float16",
  "beam_size": 3,
  "best_of": 3,
  "min_duration": 0.3
}
```

### Example 3: Long Dictations with Auto-Format
```json
{
  "hotkey": "f15",
  "language": null,
  "model": "large-v3",
  "microphone_gain": 2.0,
  "noise_threshold": 0.02,
  "vad_filter": true,
  "vad_parameters": {
    "threshold": 0.5,
    "min_speech_duration_ms": 250,
    "max_speech_duration_s": 60
  },
  "auto_format": true,
  "format_style": "natural"
}
```

### Example 4: Noisy Environment
```json
{
  "hotkey": "f15",
  "language": "zh",
  "model": "large-v3",
  "microphone_gain": 2.5,
  "noise_threshold": 0.02,
  "vad_filter": true,
  "vad_parameters": {
    "threshold": 0.6,
    "min_speech_duration_ms": 500
  }
}
```

---

## 6. TROUBLESHOOTING WITH CONFIG

### Problem: "No speech detected"
```json
{
  "microphone_gain": 2.0,
  "noise_threshold": 0.005,
  "vad_filter": false
}
```

### Problem: "Transcribing room noise"
```json
{
  "noise_threshold": 0.03,
  "vad_filter": true,
  "vad_parameters": {
    "threshold": 0.7
  }
}
```

### Problem: "Too slow"
```json
{
  "model": "medium",
  "beam_size": 3,
  "best_of": 3
}
```

### Problem: "Cuts off end of speech"
```json
{
  "min_duration": 0.3,
  "vad_filter": false
}
```

---

## 7. SWITCHING BETWEEN CONFIGS

You can have multiple config files:
- `config-fast.json` - Quick notes
- `config-accurate.json` - Important documents
- `config-noisy.json` - Coffee shop use

To use a different config:
1. Copy it to `config.json`
2. Restart dictation

Or create batch files:
```batch
@echo off
copy config-accurate.json config.json
start-dictation.bat
```

---

## Summary of Key Settings

| Setting | Purpose | Default | Recommended |
|---------|---------|---------|-------------|
| `model` | Accuracy level | `"large-v3"` | `"large-v3"` |
| `language` | Speech language | `null` | `null` for mixed |
| `microphone_gain` | Volume boost | `1.0` | `1.5-2.0` if quiet |
| `noise_threshold` | Silence level | `0.01` | `0.02` if noisy |
| `vad_filter` | Auto trim | `true` | `true` |
| `min_duration` | Min recording | `0.5` | `0.5` |
| `auto_format` | GPT formatting | `false` | `true` for long |

---

**Next:** Edit `config.json` and experiment with these settings!
