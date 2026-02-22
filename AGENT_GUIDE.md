# AGENT GUIDE: Whisper Dictation

**Target Audience**: AI Agents (OpenCode, Antigravity, etc.) & Human Developers
**Goal**: Provide immediate context on the project's architecture, key decisions, and known issues.

## 🎯 Project Objective
A universal, highly compatible voice dictation tool for Windows that works in **all** applications, including games (DirectX) and elevated windows (Task Manager).

## 🛠️ Key Technical Decisions

### 1. Input Methods & Compatibility
- **Primary API (`unicode`)**: `dictation-universal.py` uses `ctypes` to call `SendInput` with `KEYEVENTF_UNICODE` by default.
    - **Why**: `keyboard` library often fails in games or elevated apps. Must run as **Administrator** for UIPI bypass. Auto-elevation is handled via `start-universal.bat`.
    - **Constraint**: Many modern UWP / WinUI 3 applications (e.g., Fluent Search, Windows Search) completely ignore low-level `KEYEVENTF_UNICODE` injections.
- **Modern App Fallback (`clipboard`)**: For UWP apps, users should select the `clipboard` input method in `settings_gui.py`.
    - **Implementation**: Instead of naive text replacement, the application uses a **Stateful Backup and Restore Mechanism**. Before triggering `Ctrl+V`, it temporarily saves the user's existing physical clipboard content to memory, pastes the voice dictation, waits `0.15s` for the OS to register the paste event, and then seamlessly restores the user's original clipboard content. This prevents dictation from destroying user clipboard history.

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
- **Goal**: Refine raw speech text (grammar, tone, formatting) using LLMs.
- **Architecture**:
    - **Modular Profiles**: The system uses a "Three Pillars" approach: **Persona**, **Style**, and **Translation**. These are distinct text templates that are concatenated at runtime.
    - **Language Preservation Directive**: If Translation is "None", the system injects a strict global directive preventing the AI from automatically translating between languages (e.g., CN to EN) to preserve natural bilingual code-switching.
    - **Custom Prompts**: Users can define, save, and delete custom items for each pillar in the GUI. These save to `config.json` under `ai_custom_personas`, `ai_custom_styles`, etc.
    - **Quick Profiles**: Combinations of the three pillars can be saved as named profiles (`ai_saved_profiles`) and switched effortlessly from the Windows System Tray menu without opening settings.
- **Implementation**:
    - `ai_helper.py`: Constructs the dynamic system prompt and handles API requests.
    - `settings_gui.py`: Manages the UI for the three pillars and custom definitions.
    - `dictation-universal.py`: Manages the System Tray menu logic for dynamic profile switching.
- **Dependencies**: Requires `openai` module (compatible with OpenAI, DeepSeek, Gemini).

### 5. Settings GUI Rendering
- **Problem**: The `customtkinter` window sometimes spawns off-center (e.g., top-left) because `winfo_width()` returns placeholder values before the window finishes rendering natively on Windows.
- **Solution**: Hardcode the known initial fallback dimensions (`640x800`) into the centering geometry math to guarantee a perfectly centered spawn.

## 📁 Deployment & File Structure
- **Deployment Script (`build_exe.py`)**: The project uses `PyInstaller` to compile the Python application and all its heavy ML dependencies (faster-whisper, ctranslate2, torch) into a single standalone directory (`dist/VoicePro`) containing `VoicePro.exe`. This allows for true portability without end-users needing to install Python.
- `dictation-universal.py`: **Main Application**.
- `ai_helper.py`: **AI Client Module**.
- `ai_presets.py`: **Hardcoded Defaults for Personas, Styles, and Translations**.
- `start-universal.bat`: **Launcher** (Elevates to Admin and runs the `VoicePro.exe` build).
- `settings_gui.py`: Configuration UI.

## ⚠️ Known Issues
- **Notepad Input**: Requires small `time.sleep(0.01)` between chars (already implemented).
- **Anti-Cheat**: Some games unhook global keyboard hooks. We have a (disabled) watchdog for this, but currently rely on "Smart Latch" to mitigate input loss.

## 🚀 Future Development
- **Context-Aware Dictation (Vision API)**:
    - **Concept**: Capture a screenshot (or foreground window context) just before dictation is sent to the AI.
    - **Purpose**: Allow the LLM to understand the user's current environment (e.g., writing code in VSCode vs. writing an email in Outlook) to auto-adjust tone, terminology, and formatting.
    - **Requires**: Multimodal models (GPT-4o, Claude 3.5 Sonnet), `Pillow`/`mss` for fast screen capture, and privacy controls in the Settings GUI.
- **Preferences**:
    - **Language**: Python 3.10+
    - **Audio Engine**: `sounddevice` + `numpy`
    - **Model**: `faster-whisper` (CTranslate2) for performance.
    - **UI**: `tkinter` (keep it simple/native).
