#!/usr/bin/env python3
"""
Modern Settings GUI for Whisper Dictation.

Built with customtkinter for a premium, futuristic dark interface
with rounded corners, smooth switches, and segmented controls.
"""

import json
import os
import tkinter as tk
import customtkinter as ctk

from ai_presets import AI_PERSONAS, AI_STYLES, AI_TRANSLATIONS


CONFIG_FILE = "config.json"

# ============ OPTIONS ============

MODELS = ["tiny", "base", "small", "medium", "large-v2", "large-v3", "auto"]
COMPUTE_TYPES = ["float16", "int8", "auto"]
DEVICES = ["cuda", "cpu", "auto"]
LANGUAGES = [
    ("Auto-detect", None), ("Chinese (中文)", "zh"), ("English", "en"),
    ("Japanese (日本語)", "ja"), ("Korean (한국어)", "ko"), ("French", "fr"),
    ("German", "de"), ("Spanish", "es"), ("Russian", "ru"), ("Arabic", "ar"),
    ("Portuguese", "pt"), ("Italian", "it"), ("Vietnamese", "vi"),
    ("Thai", "th"), ("Indonesian", "id"), ("Hindi", "hi"),
]
OUTPUT_MODES = ["type", "clipboard", "both"]
FORMALITY_LEVELS = ["casual", "formal", "business"]
PRIMARY_LANGS = [("Auto", "auto"), ("Chinese", "zh"), ("English", "en"), ("Mixed", "mixed")]
INPUT_METHODS = ["unicode", "keyboard", "clipboard"]

AI_PROVIDERS = {
    "--- International ---": {"url": "", "model": ""},
    "DeepSeek (Global)": {"url": "https://api.deepseek.com/v1", "model": "deepseek-chat"},
    "Groq": {"url": "https://api.groq.com/openai/v1", "model": "llama-3.3-70b-versatile"},
    "Together AI": {"url": "https://api.together.xyz/v1", "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo"},
    "OpenRouter": {"url": "https://openrouter.ai/api/v1", "model": "meta-llama/llama-3.3-70b-instruct:free"},
    "Google AI Studio": {"url": "https://generativelanguage.googleapis.com/v1beta/openai", "model": "gemini-2.5-flash"},
    "Fireworks AI": {"url": "https://api.fireworks.ai/inference/v1", "model": "accounts/fireworks/models/llama-v3p3-70b-instruct"},
    "Anthropic": {"url": "https://api.anthropic.com/v1", "model": "claude-3-5-haiku-20241022"},
    "OpenAI": {"url": "https://api.openai.com/v1", "model": "gpt-4o-mini"},
    "Mistral": {"url": "https://api.mistral.ai/v1", "model": "open-mistral-nemo"},
    "SiliconFlow (Global)": {"url": "https://api.siliconflow.cn/v1", "model": "deepseek-ai/DeepSeek-V3"},
    "--- Mainland China ---": {"url": "", "model": ""},
    "ByteDance / Doubao": {"url": "https://ark.cn-beijing.volces.com/api/v3", "model": "doubao-lite-32k"},
    "Alibaba / Qwen": {"url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "model": "qwen-plus"},
    "Zhipu AI / GLM": {"url": "https://open.bigmodel.cn/api/paas/v4", "model": "glm-4-flash"},
    "Baidu / ERNIE": {"url": "https://qianfan.baidubce.com/v2", "model": "ernie-speed-128k"},
    "DeepSeek (Mainland)": {"url": "https://api.deepseek.com/v1", "model": "deepseek-chat"},
    "Tencent / Hunyuan": {"url": "https://api.hunyuan.cloud.tencent.com/v1", "model": "hunyuan-lite"},
    "Moonshot / Kimi": {"url": "https://api.moonshot.cn/v1", "model": "moonshot-v1-8k"},
    "MiniMax": {"url": "https://api.minimax.chat/v1", "model": "abab6.5s-chat"},
    "SenseTime / SenseNova": {"url": "https://api.sensenova.cn/compatible-mode/v1", "model": "SenseChat-5"},
    "01.AI / Yi": {"url": "https://api.lingyiwanwu.com/v1", "model": "yi-spark"}
}

# ============ TOOLTIPS ============

TIPS = {
    "hotkey": "Key to hold while speaking (e.g. f15, f13)",
    "pause_hotkey": "Key to toggle pause/resume",
    "model": "tiny/base = fast, large-v3 = best accuracy, auto = picks by GPU",
    "compute_type": "float16 = GPU, int8 = CPU, auto = auto-detect",
    "device": "cuda = NVIDIA GPU, cpu = universal, auto = best available",
    "language": "Force a language or auto-detect per utterance",
    "enable_punctuation": "Auto-add 。，. , ! ? punctuation",
    "enable_formatting": "Paragraph breaks and CJK-Latin spacing",
    "enable_capitalization": "Capitalize English sentences",
    "max_line_length": "Max chars per line when formatting is on",
    "output_mode": "type = keyboard, clipboard = copy, both = type + copy",
    "input_method": "unicode = standard, keyboard = legacy, clipboard = ctrl+v paste",
    "sample_rate": "Audio Hz (16000 optimal for Whisper)",
    "audio_threshold": "Min mic level for startup test",
    "min_duration": "Ignore recordings shorter than this (sec)",
    "auto_minimize_console": "Minimize console after model loads",
    "sound_feedback": "Beep on record start and processing",
    "initial_prompt": "Vocabulary hint — use bilingual text for mixed input",
    "beam_size": "Search width (1-10). Higher = more accurate",
    "best_of": "Candidates per beam step (1-10)",
    "temperature": "Sampling temp. List = auto fallback: [0, 0.2, 0.4, 0.6, 0.8, 1.0]",
    "condition_on_previous_text": "Use prior output as context (helps coherence)",
    "repetition_penalty": "1.0=off, 1.1=mild — prevents hallucination loops",
    "no_repeat_ngram_size": "Block repeating N-grams (0=off, 3=recommended)",
    "no_speech_threshold": "Skip segments with high no-speech probability",
    "log_prob_threshold": "Reject low-confidence output",
    "compression_ratio_threshold": "Reject gibberish (high ratio = bad)",
    "hallucination_silence_threshold": "Skip silent segments to prevent false text (sec)",
    "vad_filter": "Filter non-speech segments with VAD",
    "vad_threshold": "Speech detection sensitivity (lower = more sensitive)",
    "vad_min_silence": "Min silence to split segments (ms)",
    "vad_min_speech": "Min speech to keep (ms)",
    "vad_max_speech": "Max single segment duration (sec)",
}


# ============ THEME COLORS ============

# Deep space theme
COLORS = {
    "bg_dark": "#0a0a1a",
    "bg_card": "#12122a",
    "bg_input": "#1a1a35",
    "border": "#2a2a4a",
    "accent": "#6c5ce7",
    "accent_hover": "#7c6cf7",
    "accent_glow": "#2a2a4a",  # Replaced alpha glow with solid dark blue
    "text": "#e8e8f0",
    "text_dim": "#8888aa",
    "text_muted": "#555577",
    "success": "#00d2a0",
    "warning": "#ffd166",
    "danger": "#ff6b6b",
    "cyan": "#00d4ff",
    "section_gradient_start": "#6c5ce7",
    "section_gradient_end": "#00d4ff",
}


# ============ TOOLTIP ============

class ModernTooltip:
    """Sleek floating tooltip."""

    def __init__(self, widget, text: str):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, event=None):
        if self.tip:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self.tip = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-alpha", 0.95)
        frame = tk.Frame(tw, bg=COLORS["bg_card"], bd=0, highlightthickness=1,
                         highlightbackground=COLORS["accent"])
        frame.pack()
        tk.Label(frame, text=self.text, justify="left",
                 bg=COLORS["bg_card"], fg=COLORS["text_dim"],
                 font=("Segoe UI", 9), padx=10, pady=6,
                 wraplength=320).pack()

    def _hide(self, event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None


# ============ SETTINGS APP ============

class SettingsApp(ctk.CTk):
    """Modern futuristic settings window."""

    def __init__(self, config: dict, on_save=None):
        super().__init__()
        self.cfg = config.copy()
        self.on_save = on_save
        self.vars = {}

        # ---- Window ----
        self.title("Whisper Dictation — Settings")
        self.geometry("640x800")
        self.minsize(560, 600)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.configure(fg_color=COLORS["bg_dark"])

        # ---- Header ----
        header = ctk.CTkFrame(self, fg_color="transparent", height=70)
        header.pack(fill="x", padx=24, pady=(20, 0))
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="⚡ Whisper Dictation",
                     font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
                     text_color=COLORS["text"]).pack(side="left")

        ctk.CTkLabel(header, text="SETTINGS",
                     font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                     text_color=COLORS["accent"],
                     corner_radius=6,
                     fg_color=COLORS["accent_glow"],
                     padx=10, pady=2).pack(side="left", padx=(12, 0))

        # ---- Scrollable body ----
        self.body = ctk.CTkScrollableFrame(
            self, fg_color=COLORS["bg_dark"],
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["accent"],
        )
        self.body.pack(fill="both", expand=True, padx=16, pady=(12, 0))

        # ---- Build sections ----
        self._build_hotkeys()
        self._build_model()
        self._build_text_processing()
        self._build_output_audio()
        self._build_transcription()
        self._build_quality()
        self._build_vad()
        self._build_profile()
        self._build_ai_polish()

        # ---- Footer ----
        footer = ctk.CTkFrame(self, fg_color="transparent", height=56)
        footer.pack(fill="x", padx=24, pady=(8, 16))
        footer.pack_propagate(False)

        ctk.CTkButton(footer, text="Reset Defaults", width=130, height=38,
                      fg_color="transparent", border_width=1,
                      border_color=COLORS["border"],
                      hover_color=COLORS["bg_input"],
                      text_color=COLORS["text_dim"],
                      font=ctk.CTkFont(size=12),
                      command=self._on_reset).pack(side="left")

        ctk.CTkLabel(footer, text="⚠ Model changes need restart",
                     text_color=COLORS["warning"],
                     font=ctk.CTkFont(size=11)).pack(side="left", padx=(16, 0))

        ctk.CTkButton(footer, text="Save & Apply", width=140, height=38,
                      fg_color=COLORS["accent"],
                      hover_color=COLORS["accent_hover"],
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._on_save).pack(side="right")

        # Center on screen
        self.update_idletasks()
        win_w = 640
        win_h = 800
        x = (self.winfo_screenwidth() // 2) - (win_w // 2)
        y = (self.winfo_screenheight() // 2) - (win_h // 2)
        self.geometry(f"{win_w}x{win_h}+{x}+{y}")

    # ============ SECTION BUILDERS ============

    def _card(self, title: str) -> ctk.CTkFrame:
        """Create a styled section card."""
        card = ctk.CTkFrame(self.body, fg_color=COLORS["bg_card"],
                            corner_radius=12, border_width=1,
                            border_color=COLORS["border"])
        card.pack(fill="x", pady=(0, 12))

        # Section header
        hdr = ctk.CTkFrame(card, fg_color="transparent", height=36)
        hdr.pack(fill="x", padx=16, pady=(14, 6))
        hdr.pack_propagate(False)

        ctk.CTkLabel(hdr, text=title,
                     font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                     text_color=COLORS["cyan"]).pack(side="left")

        return card

    def _row(self, parent, label: str, key: str = None) -> ctk.CTkFrame:
        """Create a label + widget row with optional tooltip."""
        row = ctk.CTkFrame(parent, fg_color="transparent", height=36)
        row.pack(fill="x", padx=16, pady=3)

        lbl = ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=12),
                           text_color=COLORS["text_dim"], anchor="w")
        lbl.pack(side="left")
        if key and key in TIPS:
            ModernTooltip(lbl, TIPS[key])

        return row

    def _label(self, parent, text):
        lbl = ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=12, weight="bold"),
                           text_color=COLORS["text"], anchor="w")
        lbl.pack(fill="x", padx=16, pady=(8, 2))
        return lbl

    def _entry(self, parent, label, key, width=140, default=None, **kwargs):
        row = self._row(parent, label, key)
        val = default if default is not None else self.cfg.get(key, "")
        self.vars[key] = ctk.StringVar(value=str(val))
        ctk.CTkEntry(row, textvariable=self.vars[key], width=width,
                     fg_color=COLORS["bg_input"], border_color=COLORS["border"],
                     text_color=COLORS["text"],
                     font=ctk.CTkFont(size=12), **kwargs).pack(side="right")

    def _dropdown(self, parent, label, key, values, width=160, default=None):
        row = self._row(parent, label, key)
        val = default if default is not None else str(self.cfg.get(key, values[0]))
        self.vars[key] = ctk.StringVar(value=val)
        ctk.CTkOptionMenu(row, variable=self.vars[key], values=values, width=width,
                          fg_color=COLORS["bg_input"],
                          button_color=COLORS["accent"],
                          button_hover_color=COLORS["accent_hover"],
                          dropdown_fg_color=COLORS["bg_card"],
                          dropdown_hover_color=COLORS["accent"],
                          text_color=COLORS["text"],
                          font=ctk.CTkFont(size=12)).pack(side="right")

    def _switch(self, parent, label, key):
        row = self._row(parent, label, key)
        self.vars[key] = ctk.BooleanVar(value=self.cfg.get(key, True))
        ctk.CTkSwitch(row, text="", variable=self.vars[key], width=44,
                      fg_color=COLORS["border"],
                      progress_color=COLORS["accent"],
                      button_color=COLORS["text"],
                      button_hover_color=COLORS["accent_hover"]).pack(side="right")

    def _slider(self, parent, label, key, from_, to, step=1, default=None, width=140):
        row = self._row(parent, label, key)
        val = default if default is not None else self.cfg.get(key, from_)

        val_label = ctk.CTkLabel(row, text=str(val), width=50,
                                 font=ctk.CTkFont(size=11, weight="bold"),
                                 text_color=COLORS["accent"])
        val_label.pack(side="right")

        self.vars[key] = ctk.DoubleVar(value=float(val))

        def _update(v):
            # Round to step precision
            rounded = round(float(v) / step) * step
            if step >= 1:
                rounded = int(rounded)
            self.vars[key].set(rounded)
            val_label.configure(text=str(rounded))

        slider = ctk.CTkSlider(row, from_=from_, to=to, width=width,
                               variable=self.vars[key],
                               fg_color=COLORS["bg_input"],
                               progress_color=COLORS["accent"],
                               button_color=COLORS["text"],
                               button_hover_color=COLORS["accent_hover"],
                               command=_update)
        slider.pack(side="right", padx=(0, 8))
        _update(val)

    def _spinbox(self, parent, label, key, from_, to, step=1, default=None, width=100, **kwargs):
        """Numeric entry with arrows for fine-grained control."""
        row = self._row(parent, label, key)
        val = default if default is not None else self.cfg.get(key, from_)
        self.vars[key] = ctk.StringVar(value=str(val))

        frame = ctk.CTkFrame(row, fg_color="transparent")
        frame.pack(side="right")

        entry = ctk.CTkEntry(frame, textvariable=self.vars[key], width=width,
                             fg_color=COLORS["bg_input"], border_color=COLORS["border"],
                             text_color=COLORS["text"], justify="center",
                             font=ctk.CTkFont(size=12), **kwargs)
        entry.pack(side="left")

    # ============ SECTIONS ============

    def _build_hotkeys(self):
        c = self._card("⌨  HOTKEYS")
        self._entry(c, "Record hotkey", "hotkey", width=120)
        self._entry(c, "Pause hotkey", "pause_hotkey", width=120)
        # Bottom padding
        ctk.CTkFrame(c, fg_color="transparent", height=8).pack()

    def _build_model(self):
        c = self._card("🧠  MODEL & DEVICE")
        self._dropdown(c, "Model", "model", MODELS)
        self._dropdown(c, "Compute type", "compute_type", COMPUTE_TYPES)
        self._dropdown(c, "Device", "device", DEVICES)

        # Language selector
        row = self._row(c, "Language", "language")
        lang_names = [n for n, _ in LANGUAGES]
        self._lang_values = [v for _, v in LANGUAGES]
        self._lang_names = lang_names
        cur = self.cfg.get("language")
        cur_idx = self._lang_values.index(cur) if cur in self._lang_values else 0
        self.vars["_lang"] = ctk.StringVar(value=lang_names[cur_idx])
        ctk.CTkOptionMenu(row, variable=self.vars["_lang"], values=lang_names, width=200,
                          fg_color=COLORS["bg_input"],
                          button_color=COLORS["accent"],
                          button_hover_color=COLORS["accent_hover"],
                          dropdown_fg_color=COLORS["bg_card"],
                          dropdown_hover_color=COLORS["accent"],
                          text_color=COLORS["text"]).pack(side="right")
        ctk.CTkFrame(c, fg_color="transparent", height=8).pack()

    def _build_text_processing(self):
        c = self._card("📝  TEXT PROCESSING")
        self._switch(c, "Auto-punctuation", "enable_punctuation")
        self._switch(c, "Smart formatting", "enable_formatting")
        self._switch(c, "Auto-capitalization", "enable_capitalization")
        self._switch(c, "Enable local history logging", "enable_history_logging")
        self._slider(c, "Max line length", "max_line_length", 40, 200, step=10)
        ctk.CTkFrame(c, fg_color="transparent", height=8).pack()

    def _build_output_audio(self):
        c = self._card("📤  OUTPUT & AUDIO")
        self._dropdown(c, "Output mode", "output_mode", OUTPUT_MODES)
        self._dropdown(c, "Input method", "input_method", INPUT_METHODS)
        self._spinbox(c, "Sample rate (Hz)", "sample_rate", 8000, 48000, step=8000)
        self._spinbox(c, "Audio threshold", "audio_threshold", 0.001, 0.5, step=0.005)
        self._spinbox(c, "Min recording (sec)", "min_duration", 0.1, 5.0, step=0.1)
        self._switch(c, "Auto-minimize console", "auto_minimize_console")
        self._switch(c, "Launch at startup", "launch_at_startup")
        self._switch(c, "Sound feedback (beeps)", "sound_feedback")
        ctk.CTkFrame(c, fg_color="transparent", height=8).pack()

    def _build_transcription(self):
        c = self._card("⚙  TRANSCRIPTION")

        # Initial prompt (wide entry)
        row = self._row(c, "Initial prompt", "initial_prompt")
        self.vars["initial_prompt"] = ctk.StringVar(
            value=self.cfg.get("initial_prompt") or "")
        ctk.CTkEntry(row, textvariable=self.vars["initial_prompt"], width=280,
                     fg_color=COLORS["bg_input"], border_color=COLORS["border"],
                     text_color=COLORS["text"], placeholder_text="Bilingual hint...",
                     font=ctk.CTkFont(size=11)).pack(side="right")

        self._slider(c, "Beam size", "beam_size", 1, 10, step=1, default=self.cfg.get("beam_size", 5))
        self._slider(c, "Best of", "best_of", 1, 10, step=1, default=self.cfg.get("best_of", 5))

        # Temperature (special field)
        row = self._row(c, "Temperature", "temperature")
        temp = self.cfg.get("temperature", [0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
        temp_str = ", ".join(str(t) for t in temp) if isinstance(temp, list) else str(temp)
        self.vars["temperature"] = ctk.StringVar(value=temp_str)
        ctk.CTkEntry(row, textvariable=self.vars["temperature"], width=220,
                     fg_color=COLORS["bg_input"], border_color=COLORS["border"],
                     text_color=COLORS["text"],
                     placeholder_text="0, 0.2, 0.4, 0.6, 0.8, 1.0",
                     font=ctk.CTkFont(size=11)).pack(side="right")

        self._switch(c, "Condition on previous text", "condition_on_previous_text")
        self._spinbox(c, "Repetition penalty", "repetition_penalty", 1.0, 2.0, step=0.05,
                      default=self.cfg.get("repetition_penalty", 1.1))
        self._slider(c, "No-repeat N-gram", "no_repeat_ngram_size", 0, 10, step=1,
                     default=self.cfg.get("no_repeat_ngram_size", 3))
        ctk.CTkFrame(c, fg_color="transparent", height=8).pack()

    def _build_quality(self):
        c = self._card("🛡  QUALITY THRESHOLDS")
        self._spinbox(c, "No-speech threshold", "no_speech_threshold", 0.0, 1.0, step=0.05,
                      default=self.cfg.get("no_speech_threshold", 0.6))
        self._spinbox(c, "Log probability", "log_prob_threshold", -5.0, 0.0, step=0.1,
                      default=self.cfg.get("log_prob_threshold", -1.0))
        self._spinbox(c, "Compression ratio", "compression_ratio_threshold", 1.0, 5.0, step=0.1,
                      default=self.cfg.get("compression_ratio_threshold", 2.4))
        self._spinbox(c, "Hallucination silence (sec)", "hallucination_silence_threshold",
                      0.0, 5.0, step=0.1,
                      default=self.cfg.get("hallucination_silence_threshold", 1.0))
        ctk.CTkFrame(c, fg_color="transparent", height=8).pack()

    def _build_vad(self):
        c = self._card("🔇  VOICE ACTIVITY DETECTION")
        self._switch(c, "Enable VAD filter", "vad_filter")
        vad = self.cfg.get("vad_parameters", {})
        self._spinbox(c, "Speech threshold", "vad_threshold", 0.1, 1.0, step=0.05,
                      default=vad.get("threshold", 0.5))
        self._spinbox(c, "Min silence (ms)", "vad_min_silence", 100, 2000, step=50,
                      default=vad.get("min_silence_duration_ms", 300))
        self._spinbox(c, "Min speech (ms)", "vad_min_speech", 50, 1000, step=50,
                      default=vad.get("min_speech_duration_ms", 250))
        self._spinbox(c, "Max speech (sec)", "vad_max_speech", 5, 120, step=5,
                      default=vad.get("max_speech_duration_s", 30))
        ctk.CTkFrame(c, fg_color="transparent", height=8).pack()

    def _build_profile(self):
        c = self._card("👤  USER PROFILE")
        profile = self.cfg.get("user_profile", {})
        self._entry(c, "Name", "profile_name", width=180,
                    default=profile.get("name", ""))
        self._dropdown(c, "Primary language", "profile_language",
                       [n for n, _ in PRIMARY_LANGS], width=140,
                       default=next((n for n, v in PRIMARY_LANGS
                                     if v == profile.get("primary_language", "auto")), "Auto"))
        self._dropdown(c, "Formality", "profile_formality", FORMALITY_LEVELS, width=140,
                       default=profile.get("formality", "casual"))
        ctk.CTkFrame(c, fg_color="transparent", height=8).pack()

    def _build_ai_polish(self):
        c = self._card("✨ AI POST-PROCESSING (Polish / Refine)")
        
        # Checkbox
        var = ctk.BooleanVar(value=self.cfg.get("ai_polish_enabled", False))
        self.vars["ai_polish_enabled"] = var
        cb = ctk.CTkCheckBox(c, text="Enable AI Polish", variable=var)
        cb.pack(pady=5, anchor="w", padx=16)

        # Provider Selector
        self.vars["ai_provider"] = ctk.StringVar(value=self.cfg.get("ai_provider", "OpenAI"))
        provider_menu = ctk.CTkOptionMenu(
            c, 
            variable=self.vars["ai_provider"], 
            values=list(AI_PROVIDERS.keys()),
            width=200,
            fg_color=COLORS["bg_input"],
            button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["accent"],
            text_color=COLORS["text"],
            command=self._on_ai_provider_change
        )
        provider_menu.pack(pady=10, anchor="w", padx=16)

        self.vars["ai_api_key"] = ctk.StringVar(value=self.cfg.get("ai_api_key", ""))
        self._entry(c, "API Key (OpenAI / DeepSeek / etc)", "ai_api_key", show="*")

        self.vars["ai_base_url"] = ctk.StringVar(value=self.cfg.get("ai_base_url", "https://api.openai.com/v1"))
        self._entry(c, "Base URL", "ai_base_url")

        self.vars["ai_model"] = ctk.StringVar(value=self.cfg.get("ai_model", "gpt-4o-mini"))
        self._entry(c, "Model Name", "ai_model")

        # --- THE THREE PILLARS (Persona, Style, Translation) ---
        
        # Load custom dicts from config or default to empty
        custom_personas = self.cfg.get("ai_custom_personas", {})
        custom_styles = self.cfg.get("ai_custom_styles", {})
        custom_translations = self.cfg.get("ai_custom_translations", {})
        
        all_personas = {**AI_PERSONAS, **custom_personas}
        all_styles = {**AI_STYLES, **custom_styles}
        all_translations = {**AI_TRANSLATIONS, **custom_translations}
        
        # Add a special "Add Custom..." option to the dropdown lists
        p_list = list(all_personas.keys()) + ["---", "+ Add Custom..."]
        s_list = list(all_styles.keys()) + ["---", "+ Add Custom..."]
        t_list = list(all_translations.keys()) + ["---", "+ Add Custom..."]

        self.vars["ai_persona"] = ctk.StringVar(value=self.cfg.get("ai_persona", "None"))
        self.vars["ai_style"] = ctk.StringVar(value=self.cfg.get("ai_style", "None"))
        self.vars["ai_translation"] = ctk.StringVar(value=self.cfg.get("ai_translation", "None"))
        
        def make_custom_handler(category, custom_dict, all_dict, var, menu_widget, config_key):
            def handler(choice):
                if choice == "---":
                    var.set("None")
                elif choice == "+ Add Custom...":
                    # Prompt for Name
                    name_dialog = ctk.CTkInputDialog(text=f"Enter a short name for this custom {category}:", title="Add Custom")
                    name = name_dialog.get_input()
                    if not name or not name.strip():
                        var.set("None")
                        return
                        
                    # Prompt for Prompt Text
                    prompt_dialog = ctk.CTkInputDialog(text=f"Enter the exact prompt instruction for '{name}':\n(e.g., 'You are a cynical pirate.')", title="Add Instruction")
                    prompt_text = prompt_dialog.get_input()
                    
                    if name and prompt_text:
                        name = name.strip()
                        custom_dict[name] = prompt_text.strip()
                        self.cfg[config_key] = custom_dict
                        all_dict.update({name: prompt_text.strip()})
                        
                        # Update dropdown
                        new_values = list(all_dict.keys()) + ["---", "+ Add Custom..."]
                        menu_widget.configure(values=new_values)
                        var.set(name)
                    else:
                        var.set("None")
            return handler

        # 3-column compact layout for Persona, Style, Translation
        pillars_frame = ctk.CTkFrame(c, fg_color="transparent")
        pillars_frame.pack(pady=5, fill="x", padx=16)
        pillars_frame.columnconfigure((0, 1, 2), weight=1, uniform="pillar")

        # Column 1: Persona
        ctk.CTkLabel(pillars_frame, text="Persona", font=("", 11), text_color="#aaa").grid(row=0, column=0, sticky="w", padx=(0, 4))
        p_menu = ctk.CTkOptionMenu(pillars_frame, variable=self.vars["ai_persona"], values=p_list, width=160)
        p_menu.configure(command=make_custom_handler("Persona", custom_personas, all_personas, self.vars["ai_persona"], p_menu, "ai_custom_personas"))
        p_menu.grid(row=1, column=0, sticky="ew", padx=(0, 4))

        # Column 2: Style
        ctk.CTkLabel(pillars_frame, text="Style", font=("", 11), text_color="#aaa").grid(row=0, column=1, sticky="w", padx=4)
        s_menu = ctk.CTkOptionMenu(pillars_frame, variable=self.vars["ai_style"], values=s_list, width=160)
        s_menu.configure(command=make_custom_handler("Style", custom_styles, all_styles, self.vars["ai_style"], s_menu, "ai_custom_styles"))
        s_menu.grid(row=1, column=1, sticky="ew", padx=4)

        # Column 3: Translation
        ctk.CTkLabel(pillars_frame, text="Translation", font=("", 11), text_color="#aaa").grid(row=0, column=2, sticky="w", padx=(4, 0))
        t_menu = ctk.CTkOptionMenu(pillars_frame, variable=self.vars["ai_translation"], values=t_list, width=160)
        t_menu.configure(command=make_custom_handler("Translation", custom_translations, all_translations, self.vars["ai_translation"], t_menu, "ai_custom_translations"))
        t_menu.grid(row=1, column=2, sticky="ew", padx=(4, 0))

        # Remove Custom Button
        def remove_custom():
            curr_p = self.vars["ai_persona"].get()
            curr_s = self.vars["ai_style"].get()
            curr_t = self.vars["ai_translation"].get()
            
            deleted_any = False
            
            if curr_p in custom_personas:
                del custom_personas[curr_p]
                del all_personas[curr_p]
                self.cfg["ai_custom_personas"] = custom_personas
                self.vars["ai_persona"].set("None")
                p_menu.configure(values=list(all_personas.keys()) + ["---", "+ Add Custom..."])
                deleted_any = True
                
            if curr_s in custom_styles:
                del custom_styles[curr_s]
                del all_styles[curr_s]
                self.cfg["ai_custom_styles"] = custom_styles
                self.vars["ai_style"].set("None")
                s_menu.configure(values=list(all_styles.keys()) + ["---", "+ Add Custom..."])
                deleted_any = True
                
            if curr_t in custom_translations:
                del custom_translations[curr_t]
                del all_translations[curr_t]
                self.cfg["ai_custom_translations"] = custom_translations
                self.vars["ai_translation"].set("None")
                t_menu.configure(values=list(all_translations.keys()) + ["---", "+ Add Custom..."])
                deleted_any = True
                
            if not deleted_any:
                tk.messagebox.showinfo("Wait", "Select a custom Persona, Style, or Translation from the dropdowns first to delete it. Built-in presets cannot be deleted.")

        # Save Quick Profile
        def save_quick_profile():
            curr_p = self.vars["ai_persona"].get()
            curr_s = self.vars["ai_style"].get()
            curr_t = self.vars["ai_translation"].get()

            dialog = ctk.CTkInputDialog(text="Enter a name for this Quick Profile:", title="Save Quick Profile")
            name = dialog.get_input()
            if not name or not name.strip():
                return
            
            name = name.strip()
            
            # Load existing saved profiles
            saved_profiles = self.cfg.get("ai_saved_profiles", {})
            saved_profiles[name] = {
                "persona": curr_p,
                "style": curr_s,
                "translation": curr_t
            }
            
            self.cfg["ai_saved_profiles"] = saved_profiles
            self.cfg["ai_active_profile"] = name # Immediately set as active
            
            tk.messagebox.showinfo("Saved", f"Profile '{name}' saved successfully.\nIt will appear in the System Tray menu.")

        # Action Buttons Row
        action_frame = ctk.CTkFrame(c, fg_color="transparent")
        action_frame.pack(pady=10, fill="x", padx=16)

        ctk.CTkButton(action_frame, text="Save as Quick Profile", fg_color=COLORS["success"], hover_color="#00b88c", command=save_quick_profile).pack(side="left", padx=(0, 8))
        ctk.CTkButton(action_frame, text="Delete Selected Custom Presets", fg_color=COLORS["danger"], hover_color="#e65c5c", command=remove_custom).pack(side="left")

        # NOTE: Profile switching logic will be built into the system tray mechanism,
        # but the active baseline choices are saved here.

    def _on_ai_provider_change(self, choice):
        if choice.startswith("---"):
            return
        url = AI_PROVIDERS[choice]["url"]
        model = AI_PROVIDERS[choice]["model"]
        if url:
            self.vars["ai_base_url"].set(url)
        if model:
            self.vars["ai_model"].set(model)

    # ============ ACTIONS ============

    def _on_reset(self):
        if not tk.messagebox.askyesno("Reset", "Reset all settings to defaults?"):
            return
        self.destroy()
        try:
            import sys
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from dictation_universal import DEFAULT_CONFIG
            defaults = DEFAULT_CONFIG.copy()
        except ImportError:
            defaults = {}
        app = SettingsApp(defaults, on_save=self.on_save)
        app.mainloop()

    def _on_save(self):
        try:
            c = {}

            # Hotkeys
            c["hotkey"] = self.vars["hotkey"].get().strip().lower()
            c["pause_hotkey"] = self.vars["pause_hotkey"].get().strip().lower()

            # Model
            c["model"] = self.vars["model"].get()
            c["compute_type"] = self.vars["compute_type"].get()
            c["device"] = self.vars["device"].get()
            lang_name = self.vars["_lang"].get()
            idx = self._lang_names.index(lang_name) if lang_name in self._lang_names else 0
            c["language"] = self._lang_values[idx]

            # Text
            c["enable_punctuation"] = self.vars["enable_punctuation"].get()
            c["enable_formatting"] = self.vars["enable_formatting"].get()
            c["enable_capitalization"] = self.vars["enable_capitalization"].get()
            c["enable_history_logging"] = self.vars["enable_history_logging"].get()
            c["max_line_length"] = int(round(self.vars["max_line_length"].get()))

            # Output
            c["output_mode"] = self.vars["output_mode"].get()
            c["input_method"] = self.vars["input_method"].get()
            c["sample_rate"] = int(float(self.vars["sample_rate"].get()))
            c["audio_threshold"] = float(self.vars["audio_threshold"].get())
            c["min_duration"] = float(self.vars["min_duration"].get())
            c["auto_minimize_console"] = self.vars["auto_minimize_console"].get()
            c["launch_at_startup"] = self.vars["launch_at_startup"].get()
            c["sound_feedback"] = self.vars["sound_feedback"].get()

            # Transcription
            prompt = self.vars["initial_prompt"].get().strip()
            c["initial_prompt"] = prompt if prompt else None
            c["beam_size"] = int(round(self.vars["beam_size"].get()))
            c["best_of"] = int(round(self.vars["best_of"].get()))

            temp_str = self.vars["temperature"].get().strip()
            if "," in temp_str:
                c["temperature"] = [float(t.strip()) for t in temp_str.split(",") if t.strip()]
            else:
                c["temperature"] = float(temp_str)

            c["condition_on_previous_text"] = self.vars["condition_on_previous_text"].get()
            c["repetition_penalty"] = float(self.vars["repetition_penalty"].get())
            c["no_repeat_ngram_size"] = int(round(self.vars["no_repeat_ngram_size"].get()))

            # Quality
            c["no_speech_threshold"] = float(self.vars["no_speech_threshold"].get())
            c["log_prob_threshold"] = float(self.vars["log_prob_threshold"].get())
            c["compression_ratio_threshold"] = float(self.vars["compression_ratio_threshold"].get())
            c["hallucination_silence_threshold"] = float(self.vars["hallucination_silence_threshold"].get())

            # VAD
            c["vad_filter"] = self.vars["vad_filter"].get()
            c["vad_parameters"] = {
                "threshold": float(self.vars["vad_threshold"].get()),
                "min_silence_duration_ms": int(float(self.vars["vad_min_silence"].get())),
                "min_speech_duration_ms": int(float(self.vars["vad_min_speech"].get())),
                "max_speech_duration_s": int(float(self.vars["vad_max_speech"].get())),
            }

            # Profile
            pl_name = self.vars["profile_language"].get()
            pl_val = next((v for n, v in PRIMARY_LANGS if n == pl_name), "auto")
            c["user_profile"] = {
                "name": self.vars["profile_name"].get().strip(),
                "primary_language": pl_val,
                "formality": self.vars["profile_formality"].get(),
                "common_phrases": self.cfg.get("user_profile", {}).get("common_phrases", []),
            }

            # AI Polish
            c["ai_polish_enabled"] = self.vars["ai_polish_enabled"].get()
            c["ai_provider"] = self.vars["ai_provider"].get()
            c["ai_api_key"] = self.vars["ai_api_key"].get()
            c["ai_base_url"] = self.vars["ai_base_url"].get()
            c["ai_model"] = self.vars["ai_model"].get()
            c["ai_model"] = self.vars["ai_model"].get()
            
            c["ai_persona"] = self.vars["ai_persona"].get()
            c["ai_style"] = self.vars["ai_style"].get()
            c["ai_translation"] = self.vars["ai_translation"].get()
            
            # Carry over custom saved dicts and profiles
            c["ai_custom_personas"] = self.cfg.get("ai_custom_personas", {})
            c["ai_custom_styles"] = self.cfg.get("ai_custom_styles", {})
            c["ai_custom_translations"] = self.cfg.get("ai_custom_translations", {})
            c["ai_saved_profiles"] = self.cfg.get("ai_saved_profiles", {})
            
            # Since user clicked 'Save' in Settings UI, we assume they want these base settings active.
            # If they just created a profile, self.cfg["ai_active_profile"] will be set to it.
            # Otherwise we clear out any active quick profile so the naked dropdown selections take precedence.
            c["ai_active_profile"] = self.cfg.get("ai_active_profile", "")

            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(c, f, indent=2, ensure_ascii=False)

            if self.on_save:
                self.on_save(c)

            tk.messagebox.showinfo(
                "Saved",
                "Settings saved.\n\n"
                "• Most changes: applied immediately\n"
                "• Model/device: restart required"
            )
            self.destroy()

        except ValueError as e:
            tk.messagebox.showerror("Invalid Value", f"Check your inputs:\n{e}")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Save failed: {e}")


if __name__ == "__main__":
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    else:
        cfg = {}
    app = SettingsApp(cfg)
    app.mainloop()
