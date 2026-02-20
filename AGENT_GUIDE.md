# AGENT GUIDE: Whisper Dictation

**Target Audience**: AI Agents (OpenCode, Antigravity, etc.) & Human Developers
**Goal**: Provide immediate context on the project's architecture, key decisions, and known issues.

## 🎯 Project Objective
A universal, highly compatible voice dictation tool for Windows that works in **all** applications, including games (DirectX) and elevated windows (Task Manager).

## 🛠️ Key Technical Decisions

### 1. Input Method: `SendInput` (Win32 API)
- **Why**: `keyboard` library often fails in games or elevated apps.
- **Implementation**: [dictation-universal.py](dictation-universal.py) uses `ctypes` to call `SendInput`.
- **Constraint**: Must run as **Administrator** for UIPI bypass.
- **Auto-Elevation**: [start-universal.bat](start-universal.bat) handles this via UAC prompt.

### 2. Audio Capture: WASAPI Shared Mode
- **Why**: Games (e.g., FF7 Remake) steal exclusive control of the microphone.
- **Fix**: We force `sd.WasapiSettings(exclusive=False)` to prevent this.
- **Fallback**: If the device doesn't support WASAPI (e.g., MME drives), we fall back to default settings to avoid crash `PaErrorCode -9984`.
- **Watchdog**: A background thread monitors the stream. If it dies (0 callbacks for 5s), it restarts automatically.

### 3. Input Strategy: Smart Latch (Hybrid PTT)
- **Problem**: Some games trigger an immediate "Key Release" event (~10ms) even if the key is physically held.
- **Solution**: "Smart Latch" logic in `stop_recording`:
    - **Tap (< 0.3s)**: Toggles recording **ON** (Latched).
    - **hold (> 0.3s)**: Works as Push-to-Talk.
- **Files**: Logic sits in `dictation-universal.py` -> `stop_recording`.

### 4. AI Polish (Post-Processing)
- **Goal**: Refine raw speech text (grammar, tone, translation) using LLMs.
- **Implementation**:
    - `ai_helper.py`: Handles HTTP requests to OpenAI-compatible APIs (using `requests`).
    - `input`: Raw text from Whisper.
    - `processing`: Sends text + System Prompt to LLM.
    - `output`: Refined text replaces original text in `_output_text`.
- **Configuration**: Managed in `settings_gui.py` -> "AI Polish" tab.
- **Dependencies**: Requires `requests` library.

## 📁 File Structure
- `dictation-universal.py`: **Main Application**.
- `ai_helper.py`: **AI Client Module**.
- `start-universal.bat`: **Launcher** (use this).
- `settings_gui.py`: Configuration UI.
- `legacy/`: Archive of old/superseded scripts.

## ⚠️ Known Issues
- **Notepad Input**: Requires small `time.sleep(0.01)` between chars (already implemented).
- **Anti-Cheat**: Some games unhook global keyboard hooks. We have a (disabled) watchdog for this, but currently rely on "Smart Latch" to mitigate input loss.

## 🚀 Future Development
- **Preferences**:
    - **Language**: Python 3.10+
    - **Audio Engine**: `sounddevice` + `numpy`
    - **Model**: `faster-whisper` (CTranslate2) for performance.
    - **UI**: `tkinter` (keep it simple/native).
