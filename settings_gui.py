#!/usr/bin/env python3
"""
Settings GUI for Whisper Dictation.

A polished tkinter settings window with dark theme, tooltips,
validation, and grouped sections for all configuration options.
"""

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox


CONFIG_FILE = "config.json"

# ============ OPTION METADATA ============

MODELS = ["tiny", "base", "small", "medium", "large-v2", "large-v3", "auto"]
COMPUTE_TYPES = ["float16", "int8", "auto"]
DEVICES = ["cuda", "cpu", "auto"]
LANGUAGES = [
    ("Auto-detect", None),
    ("Chinese (中文)", "zh"),
    ("English", "en"),
    ("Japanese (日本語)", "ja"),
    ("Korean (한국어)", "ko"),
    ("French (Français)", "fr"),
    ("German (Deutsch)", "de"),
    ("Spanish (Español)", "es"),
    ("Russian (Русский)", "ru"),
    ("Arabic (العربية)", "ar"),
    ("Portuguese", "pt"),
    ("Italian (Italiano)", "it"),
    ("Dutch (Nederlands)", "nl"),
    ("Turkish (Türkçe)", "tr"),
    ("Vietnamese (Tiếng Việt)", "vi"),
    ("Thai (ภาษาไทย)", "th"),
    ("Indonesian", "id"),
    ("Hindi (हिन्दी)", "hi"),
]
OUTPUT_MODES = ["type", "clipboard", "both"]
FORMALITY_LEVELS = ["casual", "formal", "business"]
PRIMARY_LANGUAGES = [("Auto", "auto"), ("Chinese", "zh"), ("English", "en"), ("Mixed", "mixed")]

# Tooltips for every option
TOOLTIPS = {
    "hotkey": "Key to hold while speaking. Default: F15 (use a key you don't normally press).",
    "pause_hotkey": "Key to toggle pause/resume. Pausing disables the record hotkey.",
    "model": "Whisper model size. Larger = more accurate but slower and needs more VRAM.\n• tiny/base: Fast, low accuracy\n• small/medium: Balanced\n• large-v3: Best accuracy (needs 10GB+ VRAM)\n• auto: Picks based on your GPU",
    "compute_type": "Number precision for inference.\n• float16: Fast on GPU (recommended)\n• int8: Lower memory, slightly less accurate\n• auto: Picks based on device",
    "device": "Where to run the model.\n• cuda: NVIDIA GPU (fastest)\n• cpu: Works everywhere but slower\n• auto: Uses GPU if available",
    "language": "Force a specific language, or auto-detect per utterance.",
    "enable_punctuation": "Automatically add punctuation marks (。，！？ / . , ! ?) to transcribed text.",
    "enable_formatting": "Apply layout formatting like paragraph segmentation and CJK-Latin spacing.",
    "enable_capitalization": "Capitalize first letter of English sentences and the word 'I'.",
    "max_line_length": "Maximum characters per line when formatting is enabled.",
    "output_mode": "How to deliver transcribed text:\n• type: Simulate keyboard typing (works in any app)\n• clipboard: Copy to clipboard only\n• both: Type AND copy to clipboard",
    "sample_rate": "Audio sample rate in Hz. 16000 is optimal for Whisper. Don't change unless needed.",
    "audio_threshold": "Minimum microphone level to consider 'working' during the startup test.",
    "min_duration": "Ignore recordings shorter than this (seconds). Prevents accidental taps.",
    "auto_minimize_console": "Automatically minimize the console window after the model loads.",
    "sound_feedback": "Play a short beep when recording starts and when processing begins.",
    "initial_prompt": "Hint text for Whisper. Use bilingual text to improve mixed language accuracy.\nExample: '这是中文。This is English.'",
    "beam_size": "Search width during decoding. Higher = more accurate but slower. 5 is recommended.",
    "best_of": "Number of candidates per beam step. 5 is recommended for large models.",
    "temperature": "Sampling temperature. Use a list like [0, 0.2, 0.4, 0.6, 0.8, 1.0] for\nautomatic fallback: starts accurate, retries with more randomness if needed.",
    "condition_on_previous_text": "Use previous output as context for next segment.\nHelps coherence but may cause repetition loops.",
    "repetition_penalty": "Penalize repeated tokens. 1.0 = off, 1.1 = mild penalty.\nHelps prevent hallucination loops where Whisper repeats itself.",
    "no_repeat_ngram_size": "Prevent repeating N-grams of this size. 0 = disabled, 3 = recommended.\nBlocks identical 3-word phrases from appearing twice.",
    "no_speech_threshold": "If Whisper's no-speech probability exceeds this, skip the segment.",
    "log_prob_threshold": "Reject output with average log probability below this threshold.",
    "compression_ratio_threshold": "Reject output with compression ratio above this.\nHigh ratio usually means gibberish or hallucinated text.",
    "hallucination_silence_threshold": "Skip silent segments longer than this (seconds) that Whisper\nmight hallucinate content for. Very effective at reducing false output.",
    "vad_filter": "Enable Voice Activity Detection to filter out non-speech segments.",
    "vad_threshold": "VAD speech detection sensitivity. Lower = more sensitive to quiet speech.",
    "vad_min_silence": "Minimum silence duration (ms) to split speech segments.",
    "vad_min_speech": "Minimum speech duration (ms) to keep. Shorter segments are discarded.",
    "vad_max_speech": "Maximum single speech segment duration (seconds).",
    "profile_name": "Your name (for future personalization features).",
    "profile_language": "Your preferred language. Helps with formatting decisions.",
    "profile_formality": "Text style preference. Affects punctuation and formatting choices.",
}


# ============ TOOLTIP CLASS ============

class ToolTip:
    """Hover tooltip for tkinter widgets."""

    def __init__(self, widget, text: str, bg="#45475a", fg="#cdd6f4"):
        self.widget = widget
        self.text = text
        self.bg = bg
        self.fg = fg
        self.tip_window = None
        widget.bind("<Enter>", self._on_enter)
        widget.bind("<Leave>", self._on_leave)

    def _on_enter(self, event=None):
        if self.tip_window:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw, text=self.text, justify="left",
            background=self.bg, foreground=self.fg,
            relief="solid", borderwidth=1,
            font=("Segoe UI", 9), padx=8, pady=6,
            wraplength=360,
        )
        label.pack()

    def _on_leave(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


# ============ SETTINGS WINDOW ============

class SettingsWindow:
    """Polished tkinter settings window for Whisper Dictation."""

    # Catppuccin Mocha palette
    BG = "#1e1e2e"
    SURFACE = "#313244"
    OVERLAY = "#45475a"
    TEXT = "#cdd6f4"
    SUBTEXT = "#a6adc8"
    GREEN = "#a6e3a1"
    BLUE = "#89b4fa"
    YELLOW = "#f9e2af"
    RED = "#f38ba8"
    MAUVE = "#cba6f7"
    TEAL = "#94e2d5"

    def __init__(self, config: dict, on_save=None):
        self.config = config.copy()
        self.on_save = on_save
        self.root = None
        self.vars = {}

    def show(self):
        """Open the settings window."""
        self.root = tk.Tk()
        self.root.title("Whisper Dictation — Settings")
        self.root.geometry("600x760")
        self.root.resizable(True, True)
        self.root.minsize(520, 600)
        self.root.configure(bg=self.BG)

        # Try to set icon
        try:
            self.root.iconbitmap(default="")
        except Exception:
            pass

        # ---- Style ----
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background=self.BG)
        style.configure("TLabel", background=self.BG, foreground=self.TEXT, font=("Segoe UI", 10))
        style.configure("Section.TLabel", background=self.BG, foreground=self.GREEN, font=("Segoe UI", 11, "bold"))
        style.configure("Title.TLabel", background=self.BG, foreground=self.BLUE, font=("Segoe UI", 14, "bold"))
        style.configure("Hint.TLabel", background=self.BG, foreground=self.SUBTEXT, font=("Segoe UI", 8))
        style.configure("TCheckbutton", background=self.BG, foreground=self.TEXT, font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"))
        style.configure("TCombobox", fieldbackground=self.SURFACE, foreground=self.TEXT)
        style.configure("TEntry", fieldbackground=self.SURFACE, foreground=self.TEXT)
        style.configure("TSpinbox", fieldbackground=self.SURFACE, foreground=self.TEXT)
        style.map("TCheckbutton", background=[("active", self.BG)])
        style.configure("TSeparator", background=self.OVERLAY)

        # ---- Scrollable canvas ----
        outer = ttk.Frame(self.root)
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=self.BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        self.frame = ttk.Frame(canvas)

        self.frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=self.frame, anchor="nw")

        def _resize_canvas(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", _resize_canvas)

        def _mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _mousewheel)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        f = self.frame
        pad = {"padx": 16, "pady": 3}
        section_pad = {"padx": 16, "pady": (16, 4)}

        # ---- Title ----
        ttk.Label(f, text="Whisper Dictation Settings", style="Title.TLabel").pack(
            anchor="w", padx=16, pady=(16, 2))
        ttk.Label(f, text="Configure all options for your dictation tool. Hover any label for details.",
                  style="Hint.TLabel").pack(anchor="w", padx=16, pady=(0, 8))
        ttk.Separator(f).pack(fill="x", padx=16, pady=(0, 4))

        # ============ HOTKEYS ============
        self._section(f, "Hotkeys", section_pad)
        self._add_entry(f, "Record hotkey", "hotkey", pad)
        self._add_entry(f, "Pause hotkey", "pause_hotkey", pad)

        # ============ MODEL & DEVICE ============
        self._section(f, "Model & Device", section_pad)
        self._add_combo(f, "Model", "model", MODELS, pad)
        self._add_combo(f, "Compute type", "compute_type", COMPUTE_TYPES, pad)
        self._add_combo(f, "Device", "device", DEVICES, pad)

        # Language (special mapping)
        row = ttk.Frame(f)
        row.pack(fill="x", **pad)
        lbl = ttk.Label(row, text="Language")
        lbl.pack(side="left", padx=(0, 10))
        ToolTip(lbl, TOOLTIPS["language"])
        lang_names = [n for n, _ in LANGUAGES]
        self._lang_values = [v for _, v in LANGUAGES]
        self._lang_names = lang_names
        cur_lang = self.config.get("language")
        cur_idx = self._lang_values.index(cur_lang) if cur_lang in self._lang_values else 0
        self.vars["_language_name"] = tk.StringVar(value=lang_names[cur_idx])
        ttk.Combobox(row, textvariable=self.vars["_language_name"],
                     values=lang_names, state="readonly", width=25).pack(side="right")

        # ============ TEXT PROCESSING ============
        self._section(f, "Text Processing", section_pad)
        self._add_check(f, "Auto-punctuation", "enable_punctuation", pad)
        self._add_check(f, "Smart formatting", "enable_formatting", pad)
        self._add_check(f, "Auto-capitalization", "enable_capitalization", pad)
        self._add_spin(f, "Max line length", "max_line_length", 40, 200, pad)

        # ============ OUTPUT & AUDIO ============
        self._section(f, "Output & Audio", section_pad)
        self._add_combo(f, "Output mode", "output_mode", OUTPUT_MODES, pad)
        self._add_spin(f, "Sample rate (Hz)", "sample_rate", 8000, 48000, pad, increment=8000)
        self._add_spin(f, "Audio threshold", "audio_threshold", 0.001, 0.5, pad, increment=0.005)
        self._add_spin(f, "Min recording (sec)", "min_duration", 0.1, 5.0, pad, increment=0.1)
        self._add_check(f, "Auto-minimize console on startup", "auto_minimize_console", pad)
        self._add_check(f, "Sound feedback (beeps)", "sound_feedback", pad)

        # ============ TRANSCRIPTION ============
        self._section(f, "Transcription", section_pad)

        # Initial prompt (multi-line feel in single entry)
        prompt_frame = ttk.Frame(f)
        prompt_frame.pack(fill="x", **pad)
        plbl = ttk.Label(prompt_frame, text="Initial prompt")
        plbl.pack(anchor="w")
        ToolTip(plbl, TOOLTIPS["initial_prompt"])
        self.vars["initial_prompt"] = tk.StringVar(value=self.config.get("initial_prompt") or "")
        ttk.Entry(prompt_frame, textvariable=self.vars["initial_prompt"]).pack(fill="x", pady=(2, 0))

        self._add_spin(f, "Beam size", "beam_size", 1, 10, pad, default=5)
        self._add_spin(f, "Best of", "best_of", 1, 10, pad, default=5)

        # Temperature (special: could be float or list)
        temp_frame = ttk.Frame(f)
        temp_frame.pack(fill="x", **pad)
        tlbl = ttk.Label(temp_frame, text="Temperature")
        tlbl.pack(side="left", padx=(0, 10))
        ToolTip(tlbl, TOOLTIPS["temperature"])
        temp_val = self.config.get("temperature", [0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
        if isinstance(temp_val, list):
            temp_str = ", ".join(str(t) for t in temp_val)
        else:
            temp_str = str(temp_val)
        self.vars["temperature"] = tk.StringVar(value=temp_str)
        ttk.Entry(temp_frame, textvariable=self.vars["temperature"], width=28).pack(side="right")

        self._add_check(f, "Condition on previous text", "condition_on_previous_text", pad)
        self._add_spin(f, "Repetition penalty", "repetition_penalty", 1.0, 2.0, pad, increment=0.05,
                       default=self.config.get("repetition_penalty", 1.1))
        self._add_spin(f, "No-repeat N-gram size", "no_repeat_ngram_size", 0, 10, pad, default=3)

        # ============ QUALITY THRESHOLDS ============
        self._section(f, "Quality Thresholds", section_pad)
        self._add_spin(f, "No-speech threshold", "no_speech_threshold", 0.0, 1.0, pad, increment=0.05,
                       default=self.config.get("no_speech_threshold", 0.6))
        self._add_spin(f, "Log probability threshold", "log_prob_threshold", -5.0, 0.0, pad, increment=0.1,
                       default=self.config.get("log_prob_threshold", -1.0))
        self._add_spin(f, "Compression ratio threshold", "compression_ratio_threshold", 1.0, 5.0, pad, increment=0.1,
                       default=self.config.get("compression_ratio_threshold", 2.4))
        self._add_spin(f, "Hallucination silence (sec)", "hallucination_silence_threshold", 0.0, 5.0, pad,
                       increment=0.1, default=self.config.get("hallucination_silence_threshold", 1.0))

        # ============ VAD ============
        self._section(f, "Voice Activity Detection", section_pad)
        self._add_check(f, "Enable VAD filter", "vad_filter", pad)
        vad = self.config.get("vad_parameters", {})
        self._add_spin(f, "Speech threshold", "vad_threshold", 0.1, 1.0, pad, increment=0.05,
                       default=vad.get("threshold", 0.5))
        self._add_spin(f, "Min silence (ms)", "vad_min_silence", 100, 2000, pad, increment=50,
                       default=vad.get("min_silence_duration_ms", 300))
        self._add_spin(f, "Min speech (ms)", "vad_min_speech", 50, 1000, pad, increment=50,
                       default=vad.get("min_speech_duration_ms", 250))
        self._add_spin(f, "Max speech (sec)", "vad_max_speech", 5, 120, pad, increment=5,
                       default=vad.get("max_speech_duration_s", 30))

        # ============ USER PROFILE ============
        self._section(f, "User Profile", section_pad)
        profile = self.config.get("user_profile", {})
        self._add_entry(f, "Name", "profile_name", pad,
                        default=profile.get("name", ""))
        self._add_combo(f, "Primary language", "profile_language",
                        [n for n, _ in PRIMARY_LANGUAGES], pad,
                        default=next((n for n, v in PRIMARY_LANGUAGES
                                      if v == profile.get("primary_language", "auto")), "Auto"))
        self._add_combo(f, "Formality", "profile_formality", FORMALITY_LEVELS, pad,
                        default=profile.get("formality", "casual"))

        # ============ ACTION BUTTONS ============
        ttk.Separator(f).pack(fill="x", padx=16, pady=(16, 8))

        btn_row = ttk.Frame(f)
        btn_row.pack(fill="x", padx=16, pady=(4, 8))

        ttk.Button(btn_row, text="   Save & Apply   ", style="Accent.TButton",
                   command=self._on_save).pack(side="right", padx=(8, 0))
        ttk.Button(btn_row, text="   Cancel   ",
                   command=self.root.destroy).pack(side="right")
        ttk.Button(btn_row, text="   Reset to Defaults   ",
                   command=self._on_reset).pack(side="left")

        # Note
        ttk.Label(f, text="Model & device changes take effect after restart",
                  style="Hint.TLabel", foreground=self.YELLOW).pack(anchor="w", padx=16, pady=(4, 16))

        # Center window on screen
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"+{x}+{y}")

        self.root.mainloop()

    # ---- Widget helpers ----

    def _section(self, parent, title, pad):
        """Add a section header."""
        ttk.Label(parent, text=title, style="Section.TLabel").pack(anchor="w", **pad)

    def _add_entry(self, parent, label, key, pad, default=None):
        row = ttk.Frame(parent)
        row.pack(fill="x", **pad)
        lbl = ttk.Label(row, text=label)
        lbl.pack(side="left", padx=(0, 10))
        if key in TOOLTIPS:
            ToolTip(lbl, TOOLTIPS[key])
        val = default if default is not None else self.config.get(key, "")
        self.vars[key] = tk.StringVar(value=str(val))
        ttk.Entry(row, textvariable=self.vars[key], width=20).pack(side="right")

    def _add_combo(self, parent, label, key, values, pad, default=None):
        row = ttk.Frame(parent)
        row.pack(fill="x", **pad)
        lbl = ttk.Label(row, text=label)
        lbl.pack(side="left", padx=(0, 10))
        if key in TOOLTIPS:
            ToolTip(lbl, TOOLTIPS[key])
        val = default if default is not None else str(self.config.get(key, values[0]))
        self.vars[key] = tk.StringVar(value=val)
        ttk.Combobox(row, textvariable=self.vars[key], values=values,
                     state="readonly", width=22).pack(side="right")

    def _add_check(self, parent, label, key, pad):
        self.vars[key] = tk.BooleanVar(value=self.config.get(key, True))
        cb = ttk.Checkbutton(parent, text=label, variable=self.vars[key])
        cb.pack(anchor="w", **pad)
        if key in TOOLTIPS:
            ToolTip(cb, TOOLTIPS[key])

    def _add_spin(self, parent, label, key, min_val, max_val, pad, default=None, increment=1):
        row = ttk.Frame(parent)
        row.pack(fill="x", **pad)
        lbl = ttk.Label(row, text=label)
        lbl.pack(side="left", padx=(0, 10))
        if key in TOOLTIPS:
            ToolTip(lbl, TOOLTIPS[key])
        val = default if default is not None else self.config.get(key, min_val)
        self.vars[key] = tk.StringVar(value=str(val))
        ttk.Spinbox(row, textvariable=self.vars[key],
                     from_=min_val, to=max_val, increment=increment,
                     width=12).pack(side="right")

    # ---- Actions ----

    def _on_reset(self):
        """Reset all fields to DEFAULT_CONFIG values."""
        if not messagebox.askyesno("Reset", "Reset all settings to defaults?\n\nThis won't save until you click 'Save & Apply'."):
            return
        # Re-create window with default config
        self.root.destroy()
        from dictation_universal import DEFAULT_CONFIG
        win = SettingsWindow(DEFAULT_CONFIG.copy(), on_save=self.on_save)
        win.show()

    def _on_save(self):
        """Collect values and save to config.json."""
        try:
            cfg = {}

            # Hotkeys
            cfg["hotkey"] = self.vars["hotkey"].get().strip().lower()
            cfg["pause_hotkey"] = self.vars["pause_hotkey"].get().strip().lower()

            # Model & device
            cfg["model"] = self.vars["model"].get()
            cfg["compute_type"] = self.vars["compute_type"].get()
            cfg["device"] = self.vars["device"].get()

            # Language
            lang_name = self.vars["_language_name"].get()
            idx = self._lang_names.index(lang_name) if lang_name in self._lang_names else 0
            cfg["language"] = self._lang_values[idx]

            # Text processing
            cfg["enable_punctuation"] = self.vars["enable_punctuation"].get()
            cfg["enable_formatting"] = self.vars["enable_formatting"].get()
            cfg["enable_capitalization"] = self.vars["enable_capitalization"].get()
            cfg["max_line_length"] = int(float(self.vars["max_line_length"].get()))

            # Output & audio
            cfg["output_mode"] = self.vars["output_mode"].get()
            cfg["sample_rate"] = int(float(self.vars["sample_rate"].get()))
            cfg["audio_threshold"] = float(self.vars["audio_threshold"].get())
            cfg["min_duration"] = float(self.vars["min_duration"].get())
            cfg["auto_minimize_console"] = self.vars["auto_minimize_console"].get()
            cfg["sound_feedback"] = self.vars["sound_feedback"].get()

            # Initial prompt
            prompt = self.vars["initial_prompt"].get().strip()
            cfg["initial_prompt"] = prompt if prompt else None

            # Transcription
            cfg["beam_size"] = int(float(self.vars["beam_size"].get()))
            cfg["best_of"] = int(float(self.vars["best_of"].get()))

            # Temperature (parse list or single float)
            temp_str = self.vars["temperature"].get().strip()
            if "," in temp_str:
                cfg["temperature"] = [float(t.strip()) for t in temp_str.split(",") if t.strip()]
            else:
                cfg["temperature"] = float(temp_str)

            cfg["condition_on_previous_text"] = self.vars["condition_on_previous_text"].get()
            cfg["repetition_penalty"] = float(self.vars["repetition_penalty"].get())
            cfg["no_repeat_ngram_size"] = int(float(self.vars["no_repeat_ngram_size"].get()))

            # Quality thresholds
            cfg["no_speech_threshold"] = float(self.vars["no_speech_threshold"].get())
            cfg["log_prob_threshold"] = float(self.vars["log_prob_threshold"].get())
            cfg["compression_ratio_threshold"] = float(self.vars["compression_ratio_threshold"].get())
            cfg["hallucination_silence_threshold"] = float(self.vars["hallucination_silence_threshold"].get())

            # VAD
            cfg["vad_filter"] = self.vars["vad_filter"].get()
            cfg["vad_parameters"] = {
                "threshold": float(self.vars["vad_threshold"].get()),
                "min_silence_duration_ms": int(float(self.vars["vad_min_silence"].get())),
                "min_speech_duration_ms": int(float(self.vars["vad_min_speech"].get())),
                "max_speech_duration_s": int(float(self.vars["vad_max_speech"].get())),
            }

            # User profile
            pl_name = self.vars["profile_language"].get()
            pl_val = next((v for n, v in PRIMARY_LANGUAGES if n == pl_name), "auto")
            cfg["user_profile"] = {
                "name": self.vars["profile_name"].get().strip(),
                "primary_language": pl_val,
                "formality": self.vars["profile_formality"].get(),
                "common_phrases": self.config.get("user_profile", {}).get("common_phrases", []),
            }

            # Save
            with open(CONFIG_FILE, "w", encoding="utf-8") as f_out:
                json.dump(cfg, f_out, indent=2, ensure_ascii=False)

            if self.on_save:
                self.on_save(cfg)

            messagebox.showinfo(
                "Settings Saved",
                "Configuration saved.\n\n"
                "• Text, output, audio, transcription: applied immediately\n"
                "• Model & device changes: restart required"
            )
            self.root.destroy()

        except ValueError as e:
            messagebox.showerror("Invalid Value", f"Please check your inputs:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")


# ============ PUBLIC API ============

def open_settings(config: dict, on_save=None):
    """Open settings window in a new thread (non-blocking)."""
    import threading
    def _run():
        win = SettingsWindow(config, on_save=on_save)
        win.show()
    t = threading.Thread(target=_run, daemon=True)
    t.start()


if __name__ == "__main__":
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    else:
        cfg = {}
    win = SettingsWindow(cfg)
    win.show()
