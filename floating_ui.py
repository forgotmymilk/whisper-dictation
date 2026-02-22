#!/usr/bin/env python3
"""
Floating Voice Panel - Windows 11-style always-on-top microphone widget.

Runs as a standalone subprocess. Communicates with the main app
via a shared JSON state file for thread/process safety.

States:
  idle       → Glowing dark panel, green microphone icon (gentle breathing)
  recording  → Red mic, pulsing audio waveform rings react to voice volume
  processing → Amber spinning arc

Interactions:
  Left-click mic area  → Toggle recording (start/stop dictation)
  Drag the panel       → Move it anywhere on screen
  Click ⚙ gear icon   → Open Settings GUI
  Right-click          → Context menu (future)
"""

import tkinter as tk
import json
import os
import sys
import math

# ---- IPC ----
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".floating_state.json")
SETTINGS_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings_gui.py")

DEFAULT_STATE = {
    "status": "idle",
    "volume": 0.0,
    "click_action": "",
    "settings_action": "",
}


def read_state() -> dict:
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return DEFAULT_STATE.copy()


def write_action(key: str, value: str):
    """Write a single action field without overwriting the rest."""
    state = read_state()
    state[key] = value
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception:
        pass


# ---- Color palette ----
BG          = "#1a1a2e"      # Dark navy panel background
BG_LIGHT    = "#16213e"      # Slightly lighter for inner highlight
IDLE_COLOR  = "#22c55e"      # Green
REC_COLOR   = "#ef4444"      # Red
PROC_COLOR  = "#f59e0b"      # Amber
GEAR_COLOR  = "#94a3b8"      # Muted blue-grey
TEXT_DIM    = "#64748b"


class FloatingPanel:
    """Windows 11-style floating microphone panel."""

    # Panel is a tall narrow pill: 100 wide x 160 tall
    W = 100
    H = 160

    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-alpha", 0.94)   # slight translucency
        self.root.config(bg=BG)

        # Position: bottom-right area
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = sw - self.W - 60
        y = sh - self.H - 100
        self.root.geometry(f"{self.W}x{self.H}+{x}+{y}")

        # Round-ish border via Canvas
        self.canvas = tk.Canvas(
            self.root, width=self.W, height=self.H,
            bg=BG, highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        # Drag state
        self._press_x = 0
        self._press_y = 0
        self._moved = False
        self._press_time = 0.0

        self.canvas.bind("<ButtonPress-1>",   self._on_press)
        self.canvas.bind("<B1-Motion>",       self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

        # Animation
        self._frame = 0

        # Initialize state
        state = DEFAULT_STATE.copy()
        try:
            with open(STATE_FILE, "w") as f:
                json.dump(state, f)
        except Exception:
            pass

        self._animate()

    # ---- Drag / Click logic ----

    def _on_press(self, event):
        import time
        self._press_x = event.x
        self._press_y = event.y
        self._moved = False
        self._press_time = time.time()
        # Store root position at press time for dragging
        self._root_x_at_press = self.root.winfo_x()
        self._root_y_at_press = self.root.winfo_y()

    def _on_drag(self, event):
        dx = event.x - self._press_x
        dy = event.y - self._press_y
        # Only consider it a drag if moved more than 5px
        if abs(dx) > 5 or abs(dy) > 5:
            self._moved = True
            new_x = self._root_x_at_press + (event.x - self._press_x)
            new_y = self._root_y_at_press + (event.y - self._press_y)
            self.root.geometry(f"+{new_x}+{new_y}")

    def _on_release(self, event):
        import time
        if self._moved:
            return  # Was a drag, ignore click

        hold = time.time() - self._press_time
        if hold > 0.5:
            return  # Long press — ignore (could be accidental)

        # Determine what was clicked by y-coordinate
        if event.y < self.H - 30:
            # Clicked mic area → toggle recording
            write_action("click_action", "toggle_record")
        else:
            # Clicked gear/settings area (bottom 30px)
            self._open_settings()

    def _open_settings(self):
        """Open settings GUI as subprocess."""
        import subprocess
        try:
            # When bundled as exe, sys.executable IS the exe
            # We embed settings_gui.py as a data file alongside the exe
            if getattr(sys, 'frozen', False):
                # PyInstaller bundle — find scripts beside the exe
                base = os.path.dirname(sys.executable)
                script = os.path.join(base, "settings_gui.py")
                python = os.path.join(base, "_internal", "python.exe")
                if not os.path.exists(python):
                    # Try beside the exe
                    python = os.path.join(base, "python.exe")
                if not os.path.exists(python):
                    # Fallback: use embedded python from _internal
                    for dirpath, dirs, files in os.walk(base):
                        if "python.exe" in files:
                            python = os.path.join(dirpath, "python.exe")
                            break
            else:
                # Dev mode — use current interpreter
                python = sys.executable
                script = SETTINGS_SCRIPT

            subprocess.Popen(
                [python, script],
                cwd=os.path.dirname(script),
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
        except Exception as e:
            print(f"Settings open error: {e}")

    # ---- Animation ----

    def _animate(self):
        state = read_state()
        status = state.get("status", "idle")
        volume = float(state.get("volume", 0.0))

        self.canvas.delete("all")
        self._frame += 1

        # Pill background
        r_pill = 18
        self._draw_rounded_rect(0, 0, self.W, self.H, r_pill, BG, "#2d3748", 1)

        cx = self.W / 2
        mic_cy = self.H / 2 - 12   # mic center, slightly above center
        gear_y = self.H - 20        # gear center

        if status == "recording":
            self._draw_recording_state(cx, mic_cy, volume)
        elif status == "processing":
            self._draw_processing_state(cx, mic_cy)
        else:
            self._draw_idle_state(cx, mic_cy)

        # Status text
        status_text = {"idle": "Ready", "recording": "Listening...", "processing": "Thinking..."}.get(status, "")
        status_color = {"idle": IDLE_COLOR, "recording": REC_COLOR, "processing": PROC_COLOR}.get(status, GEAR_COLOR)
        self.canvas.create_text(cx, mic_cy + 38, text=status_text, fill=status_color, font=("Segoe UI", 9))

        # Divider line
        self.canvas.create_line(16, self.H - 38, self.W - 16, self.H - 38, fill="#2d3748", width=1)

        # Gear icon area (bottom)
        self._draw_gear(cx, gear_y, 8)
        self.canvas.create_text(cx + 16, gear_y, text="Settings", fill=GEAR_COLOR, font=("Segoe UI", 8), anchor="w")

        self.root.after(33, self._animate)

    # ---- Drawing Helpers ----

    def _draw_rounded_rect(self, x1, y1, x2, y2, r, fill, outline, width):
        self.canvas.create_arc(x1, y1, x1 + 2*r, y1 + 2*r, start=90,  extent=90,  fill=fill, outline=outline, width=width)
        self.canvas.create_arc(x2-2*r, y1, x2, y1+2*r,     start=0,   extent=90,  fill=fill, outline=outline, width=width)
        self.canvas.create_arc(x1, y2-2*r, x1+2*r, y2,     start=180, extent=90,  fill=fill, outline=outline, width=width)
        self.canvas.create_arc(x2-2*r, y2-2*r, x2, y2,     start=270, extent=90,  fill=fill, outline=outline, width=width)
        self.canvas.create_rectangle(x1+r, y1, x2-r, y2,   fill=fill, outline="")
        self.canvas.create_rectangle(x1, y1+r, x2, y2-r,   fill=fill, outline="")

    def _draw_mic_icon(self, cx, cy, color, scale=1.0):
        """Draw a simple microphone symbol using canvas shapes."""
        # Mic capsule (body)
        mw = int(10 * scale)
        mh = int(16 * scale)
        mr = mw // 2
        mx1, mx2 = cx - mw//2, cx + mw//2
        my1, my2 = cy - mh//2 - 2, cy + mh//2 - 4
        # Capsule top
        self.canvas.create_arc(mx1, my1, mx2, my1 + mw, start=0, extent=180, fill=color, outline=color)
        # Capsule body
        self.canvas.create_rectangle(mx1, my1 + mr, mx2, my2, fill=color, outline="")
        # Capsule bottom arc
        self.canvas.create_arc(mx1, my2 - mw, mx2, my2, start=180, extent=180, fill=color, outline=color)
        # Stand
        stand_y = my2 + int(4 * scale)
        stand_bot = stand_y + int(5 * scale)
        self.canvas.create_arc(cx - int(10*scale), my2, cx + int(10*scale), my2 + int(12*scale),
                               start=180, extent=180, outline=color, fill="", width=2)
        self.canvas.create_line(cx, my2 + int(6*scale), cx, stand_bot, fill=color, width=2)
        # Base line
        self.canvas.create_line(cx - int(7*scale), stand_bot, cx + int(7*scale), stand_bot, fill=color, width=2)

    def _draw_gear(self, cx, cy, r):
        """Draw a gear/cog icon."""
        teeth = 6
        for i in range(teeth):
            angle = (i / teeth) * math.pi * 2
            x1 = cx + math.cos(angle) * r
            y1 = cy + math.sin(angle) * r
            x2 = cx + math.cos(angle) * (r + 3)
            y2 = cy + math.sin(angle) * (r + 3)
            self.canvas.create_line(x1, y1, x2, y2, fill=GEAR_COLOR, width=2)
        self.canvas.create_oval(cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2,
                                fill=BG, outline=GEAR_COLOR, width=1)

    def _draw_idle_state(self, cx, cy):
        """Breathing green glow + microphone icon."""
        t = self._frame * 0.035
        breath = math.sin(t) * 0.5 + 0.5  # 0..1

        # Outer glow ring
        glow_r = 24 + breath * 5
        alpha_color = "#1a3a2a" if breath < 0.5 else "#1f4a33"
        self.canvas.create_oval(cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r,
                                fill=alpha_color, outline="#22c55e", width=1)

        # Inner glow
        inner_r = 18 + breath * 3
        self.canvas.create_oval(cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r,
                                fill="#16a34a", outline="#22c55e", width=2)

        self._draw_mic_icon(cx, cy - 2, "#f0fdf4", scale=1.1)

    def _draw_recording_state(self, cx, cy, volume):
        """Pulsing red rings + mic icon."""
        t = self._frame * 0.07
        scaled_vol = min(volume * 6, 1.0)

        # Expanding ripple rings
        for i in range(4):
            phase = (t + i * 0.9) % 4.0
            ring_r = 16 + phase * 14 + scaled_vol * 10
            fade = max(0.0, 1.0 - phase / 4.0)
            r_int = int(239 * fade)
            g_int = int(68 * fade)
            color = f"#{r_int:02x}{g_int:02x}68" if r_int > 10 else BG
            width = max(1, int(2.5 * fade))
            self.canvas.create_oval(cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r,
                                    fill="", outline=color, width=width)

        # Core circle
        core_r = 18 + scaled_vol * 5
        self.canvas.create_oval(cx - core_r, cy - core_r, cx + core_r, cy + core_r,
                                fill="#7f1d1d", outline=REC_COLOR, width=2)

        self._draw_mic_icon(cx, cy - 2, "#fecaca", scale=1.15)

    def _draw_processing_state(self, cx, cy):
        """Spinning amber arc + mic icon."""
        t = self._frame * 0.12
        r = 22
        # Background circle
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                fill="#451a03", outline=PROC_COLOR, width=1)

        # Spinning arc (140° arc that rotates)
        start_deg = (t * 180 / math.pi) % 360
        self.canvas.create_arc(cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2,
                               start=start_deg, extent=140,
                               style=tk.ARC, outline=PROC_COLOR, width=3)

        self._draw_mic_icon(cx, cy - 2, "#fef3c7", scale=1.1)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = FloatingPanel()
    app.run()
