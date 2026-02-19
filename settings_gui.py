#!/usr/bin/env python3
"""
Settings GUI for Whisper Dictation.

A tkinter-based settings window accessible from the system tray menu.
Reads/writes config.json and applies changes live where possible.
"""

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox


CONFIG_FILE = "config.json"

# All available options with metadata
MODELS = ["tiny", "base", "small", "medium", "large-v2", "large-v3", "auto"]
COMPUTE_TYPES = ["float16", "int8", "auto"]
DEVICES = ["cuda", "cpu", "auto"]
LANGUAGES = [
    ("Auto-detect", None),
    ("Chinese (中文)", "zh"),
    ("English", "en"),
    ("Japanese (日本語)", "ja"),
    ("Korean (한국어)", "ko"),
    ("French", "fr"),
    ("German", "de"),
    ("Spanish", "es"),
    ("Russian", "ru"),
    ("Arabic", "ar"),
]
OUTPUT_MODES = ["type", "clipboard", "both"]
FORMALITY_LEVELS = ["casual", "formal", "business"]
PRIMARY_LANGUAGES = [("Auto", "auto"), ("Chinese", "zh"), ("English", "en"), ("Mixed", "mixed")]


class SettingsWindow:
    """Tkinter settings window for Whisper Dictation."""

    def __init__(self, config: dict, on_save=None):
        """
        Args:
            config: Current configuration dict.
            on_save: Callback when settings are saved. Receives new config dict.
        """
        self.config = config.copy()
        self.on_save = on_save
        self.root = None

    def show(self):
        """Open the settings window (blocks until closed)."""
        self.root = tk.Tk()
        self.root.title("🎤 Whisper Dictation — Settings")
        self.root.geometry("560x720")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        # Dark theme colors
        style = ttk.Style()
        style.theme_use("clam")

        bg = "#1e1e2e"
        fg = "#cdd6f4"
        accent = "#89b4fa"
        field_bg = "#313244"
        section_fg = "#a6e3a1"

        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=fg, font=("Segoe UI", 10))
        style.configure("Section.TLabel", background=bg, foreground=section_fg, font=("Segoe UI", 11, "bold"))
        style.configure("TCheckbutton", background=bg, foreground=fg, font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"))
        style.configure("Save.TButton", font=("Segoe UI", 11, "bold"))
        style.configure("TCombobox", fieldbackground=field_bg, foreground=fg)
        style.configure("TEntry", fieldbackground=field_bg, foreground=fg)
        style.configure("TSpinbox", fieldbackground=field_bg, foreground=fg)
        style.map("TCheckbutton", background=[("active", bg)])

        # Scrollable content
        canvas = tk.Canvas(self.root, bg=bg, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=540)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

        # Store tk vars
        self.vars = {}

        pad = {"padx": 12, "pady": 3}
        section_pad = {"padx": 12, "pady": (14, 4)}

        # ============ HOTKEYS ============
        ttk.Label(scroll_frame, text="⌨️  Hotkeys", style="Section.TLabel").pack(anchor="w", **section_pad)

        self._add_entry(scroll_frame, "Record hotkey:", "hotkey", pad)
        self._add_entry(scroll_frame, "Pause hotkey:", "pause_hotkey", pad)

        # ============ MODEL & DEVICE ============
        ttk.Label(scroll_frame, text="🧠  Model & Device", style="Section.TLabel").pack(anchor="w", **section_pad)

        self._add_combo(scroll_frame, "Model:", "model", MODELS, pad)
        self._add_combo(scroll_frame, "Compute type:", "compute_type", COMPUTE_TYPES, pad)
        self._add_combo(scroll_frame, "Device:", "device", DEVICES, pad)

        # Language (special: display name → value mapping)
        lang_frame = ttk.Frame(scroll_frame)
        lang_frame.pack(fill="x", **pad)
        ttk.Label(lang_frame, text="Language:").pack(side="left", padx=(0, 10))
        lang_names = [name for name, _ in LANGUAGES]
        lang_values = [val for _, val in LANGUAGES]
        current_lang = self.config.get("language")
        current_idx = lang_values.index(current_lang) if current_lang in lang_values else 0
        self.vars["_language_name"] = tk.StringVar(value=lang_names[current_idx])
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.vars["_language_name"],
                                   values=lang_names, state="readonly", width=25)
        lang_combo.pack(side="right")
        self._lang_values = lang_values
        self._lang_names = lang_names

        # ============ TEXT PROCESSING ============
        ttk.Label(scroll_frame, text="📝  Text Processing", style="Section.TLabel").pack(anchor="w", **section_pad)

        self._add_check(scroll_frame, "Auto-punctuation", "enable_punctuation", pad)
        self._add_check(scroll_frame, "Smart formatting (paragraphs, line breaks)", "enable_formatting", pad)
        self._add_check(scroll_frame, "Auto-capitalization (English)", "enable_capitalization", pad)
        self._add_spinbox(scroll_frame, "Max line length:", "max_line_length", 40, 200, pad)

        # ============ OUTPUT ============
        ttk.Label(scroll_frame, text="📤  Output", style="Section.TLabel").pack(anchor="w", **section_pad)

        self._add_combo(scroll_frame, "Output mode:", "output_mode", OUTPUT_MODES, pad)

        # ============ AUDIO ============
        ttk.Label(scroll_frame, text="🎤  Audio", style="Section.TLabel").pack(anchor="w", **section_pad)

        self._add_spinbox(scroll_frame, "Min recording (sec):", "min_duration", 0.1, 5.0, pad, increment=0.1)
        self._add_spinbox(scroll_frame, "Audio threshold:", "audio_threshold", 0.001, 0.5, pad, increment=0.005)

        # ============ TRANSCRIPTION ============
        ttk.Label(scroll_frame, text="⚙️  Transcription (Advanced)", style="Section.TLabel").pack(anchor="w", **section_pad)

        self._add_spinbox(scroll_frame, "Beam size:", "beam_size", 1, 10, pad, default=5)
        self._add_spinbox(scroll_frame, "Best of:", "best_of", 1, 10, pad, default=5)
        self._add_check(scroll_frame, "Condition on previous text", "condition_on_previous_text", pad)

        # Initial prompt
        prompt_frame = ttk.Frame(scroll_frame)
        prompt_frame.pack(fill="x", **pad)
        ttk.Label(prompt_frame, text="Initial prompt:").pack(anchor="w")
        self.vars["initial_prompt"] = tk.StringVar(value=self.config.get("initial_prompt") or "")
        prompt_entry = ttk.Entry(prompt_frame, textvariable=self.vars["initial_prompt"], width=60)
        prompt_entry.pack(fill="x", pady=(2, 0))

        # ============ VAD ============
        ttk.Label(scroll_frame, text="🔇  Voice Activity Detection", style="Section.TLabel").pack(anchor="w", **section_pad)

        self._add_check(scroll_frame, "Enable VAD filter", "vad_filter", pad)
        vad = self.config.get("vad_parameters", {})
        self._add_spinbox(scroll_frame, "Speech threshold:", "vad_threshold", 0.1, 1.0, pad,
                          default=vad.get("threshold", 0.5), increment=0.05)
        self._add_spinbox(scroll_frame, "Min silence (ms):", "vad_min_silence", 100, 2000, pad,
                          default=vad.get("min_silence_duration_ms", 300), increment=50)
        self._add_spinbox(scroll_frame, "Min speech (ms):", "vad_min_speech", 50, 1000, pad,
                          default=vad.get("min_speech_duration_ms", 250), increment=50)
        self._add_spinbox(scroll_frame, "Max speech (sec):", "vad_max_speech", 5, 120, pad,
                          default=vad.get("max_speech_duration_s", 30), increment=5)

        # ============ USER PROFILE ============
        ttk.Label(scroll_frame, text="👤  User Profile", style="Section.TLabel").pack(anchor="w", **section_pad)

        profile = self.config.get("user_profile", {})
        self._add_entry(scroll_frame, "Name:", "profile_name", pad, default=profile.get("name", ""))
        self._add_combo(scroll_frame, "Primary language:", "profile_language",
                        [name for name, _ in PRIMARY_LANGUAGES], pad,
                        default=next((n for n, v in PRIMARY_LANGUAGES if v == profile.get("primary_language", "auto")), "Auto"))
        self._add_combo(scroll_frame, "Formality:", "profile_formality", FORMALITY_LEVELS, pad,
                        default=profile.get("formality", "casual"))

        # ============ BUTTONS ============
        btn_frame = ttk.Frame(scroll_frame)
        btn_frame.pack(fill="x", padx=12, pady=(20, 12))

        ttk.Button(btn_frame, text="Save & Apply", style="Save.TButton",
                   command=self._on_save).pack(side="right", padx=(8, 0))
        ttk.Button(btn_frame, text="Cancel",
                   command=self.root.destroy).pack(side="right")

        # Note
        note_label = ttk.Label(scroll_frame,
                               text="⚠️  Model/device changes take effect after restart",
                               foreground="#f9e2af")
        note_label.pack(anchor="w", padx=12, pady=(0, 12))

        self.root.mainloop()

    # ---- Widget helpers ----

    def _add_entry(self, parent, label, key, pad, default=None):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", **pad)
        ttk.Label(frame, text=label).pack(side="left", padx=(0, 10))
        val = default if default is not None else self.config.get(key, "")
        self.vars[key] = tk.StringVar(value=str(val))
        ttk.Entry(frame, textvariable=self.vars[key], width=20).pack(side="right")

    def _add_combo(self, parent, label, key, values, pad, default=None):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", **pad)
        ttk.Label(frame, text=label).pack(side="left", padx=(0, 10))
        val = default if default is not None else str(self.config.get(key, values[0]))
        self.vars[key] = tk.StringVar(value=val)
        ttk.Combobox(frame, textvariable=self.vars[key], values=values,
                      state="readonly", width=22).pack(side="right")

    def _add_check(self, parent, label, key, pad):
        self.vars[key] = tk.BooleanVar(value=self.config.get(key, True))
        ttk.Checkbutton(parent, text=label, variable=self.vars[key]).pack(anchor="w", **pad)

    def _add_spinbox(self, parent, label, key, min_val, max_val, pad, default=None, increment=1):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", **pad)
        ttk.Label(frame, text=label).pack(side="left", padx=(0, 10))
        val = default if default is not None else self.config.get(key, min_val)
        self.vars[key] = tk.StringVar(value=str(val))
        ttk.Spinbox(frame, textvariable=self.vars[key],
                     from_=min_val, to=max_val, increment=increment,
                     width=10).pack(side="right")

    # ---- Save ----

    def _on_save(self):
        """Collect all values and save to config.json."""
        try:
            # Build config dict
            new_config = {}

            # Hotkeys
            new_config["hotkey"] = self.vars["hotkey"].get().strip().lower()
            new_config["pause_hotkey"] = self.vars["pause_hotkey"].get().strip().lower()

            # Model & device
            new_config["model"] = self.vars["model"].get()
            new_config["compute_type"] = self.vars["compute_type"].get()
            new_config["device"] = self.vars["device"].get()

            # Language
            lang_name = self.vars["_language_name"].get()
            idx = self._lang_names.index(lang_name) if lang_name in self._lang_names else 0
            new_config["language"] = self._lang_values[idx]

            # Text processing
            new_config["enable_punctuation"] = self.vars["enable_punctuation"].get()
            new_config["enable_formatting"] = self.vars["enable_formatting"].get()
            new_config["enable_capitalization"] = self.vars["enable_capitalization"].get()
            new_config["max_line_length"] = int(float(self.vars["max_line_length"].get()))

            # Output
            new_config["output_mode"] = self.vars["output_mode"].get()

            # Audio
            new_config["min_duration"] = float(self.vars["min_duration"].get())
            new_config["audio_threshold"] = float(self.vars["audio_threshold"].get())

            # Transcription
            new_config["beam_size"] = int(float(self.vars["beam_size"].get()))
            new_config["best_of"] = int(float(self.vars["best_of"].get()))
            new_config["condition_on_previous_text"] = self.vars["condition_on_previous_text"].get()

            prompt = self.vars["initial_prompt"].get().strip()
            new_config["initial_prompt"] = prompt if prompt else None

            # VAD
            new_config["vad_filter"] = self.vars["vad_filter"].get()
            new_config["vad_parameters"] = {
                "threshold": float(self.vars["vad_threshold"].get()),
                "min_silence_duration_ms": int(float(self.vars["vad_min_silence"].get())),
                "min_speech_duration_ms": int(float(self.vars["vad_min_speech"].get())),
                "max_speech_duration_s": int(float(self.vars["vad_max_speech"].get())),
            }

            # User profile
            pl_name = self.vars["profile_language"].get()
            pl_val = next((v for n, v in PRIMARY_LANGUAGES if n == pl_name), "auto")
            new_config["user_profile"] = {
                "name": self.vars["profile_name"].get().strip(),
                "primary_language": pl_val,
                "formality": self.vars["profile_formality"].get(),
                "common_phrases": self.config.get("user_profile", {}).get("common_phrases", []),
            }

            # Save to file
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(new_config, f, indent=2, ensure_ascii=False)

            if self.on_save:
                self.on_save(new_config)

            messagebox.showinfo("Settings Saved",
                                "Configuration saved to config.json.\n\n"
                                "Model/device changes require restart.\n"
                                "Other changes take effect immediately.")
            self.root.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")


def open_settings(config: dict, on_save=None):
    """Open settings window in a new thread (non-blocking)."""
    import threading
    def _run():
        win = SettingsWindow(config, on_save=on_save)
        win.show()
    t = threading.Thread(target=_run, daemon=True)
    t.start()


if __name__ == "__main__":
    # Standalone test
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    else:
        cfg = {}
    win = SettingsWindow(cfg)
    win.show()
