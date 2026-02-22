#!/usr/bin/env python3
"""
Floating Voice Indicator - Always-on-top desktop widget.

Runs as a standalone subprocess. Communicates with the main app
via a shared JSON state file for thread/process safety.

States:
  idle      → Green pulsing orb (breathing animation)
  recording → Red expanding rings (voice waveform)
  processing → Amber spinning indicator

Click the orb to toggle recording (sends signal back to main app).
"""

import tkinter as tk
import json
import os
import sys
import time
import math

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".floating_state.json")

# Default state
DEFAULT_STATE = {
    "status": "idle",      # idle | recording | processing
    "volume": 0.0,         # 0.0 - 1.0 RMS volume level
    "click_action": "",    # "" | "toggle_record" (written by UI, read by main app)
}


def read_state() -> dict:
    """Read shared state from file."""
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return DEFAULT_STATE.copy()


def write_state(state: dict):
    """Write shared state to file."""
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except IOError:
        pass


class FloatingOrb:
    """A sleek, animated desktop indicator."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)

        # Transparent background
        self.bg_color = "#000001"
        self.root.wm_attributes("-transparentcolor", self.bg_color)
        self.root.config(bg=self.bg_color)

        # Dimensions
        self.size = 64
        self.root.geometry(self._initial_geometry())

        # Canvas
        self.canvas = tk.Canvas(
            self.root, width=self.size, height=self.size,
            bg=self.bg_color, highlightthickness=0
        )
        self.canvas.pack()

        # Dragging support
        self._drag_data = {"x": 0, "y": 0}
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

        # Animation state
        self._frame = 0
        self._was_dragged = False

        # Initialize state file
        write_state(DEFAULT_STATE)

        # Start animation loop
        self._animate()

    def _initial_geometry(self) -> str:
        """Position at bottom-right of screen."""
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = screen_w - self.size - 80
        y = screen_h - self.size - 120
        return f"{self.size}x{self.size}+{x}+{y}"

    # ---- Drag & Click ----

    def _on_press(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        self._was_dragged = False

    def _on_drag(self, event):
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        x = self.root.winfo_x() + dx
        y = self.root.winfo_y() + dy
        self.root.geometry(f"+{x}+{y}")
        self._was_dragged = True

    def _on_release(self, event):
        if not self._was_dragged:
            # This was a click, not a drag → toggle recording
            self._send_click_action()

    def _send_click_action(self):
        """Signal the main app to toggle recording."""
        state = read_state()
        state["click_action"] = "toggle_record"
        write_state(state)

    # ---- Animation ----

    def _animate(self):
        state = read_state()
        status = state.get("status", "idle")
        volume = state.get("volume", 0.0)

        self.canvas.delete("all")
        cx, cy = self.size / 2, self.size / 2
        self._frame += 1

        if status == "recording":
            self._draw_recording(cx, cy, volume)
        elif status == "processing":
            self._draw_processing(cx, cy)
        else:
            self._draw_idle(cx, cy)

        self.root.after(33, self._animate)  # ~30 FPS

    def _draw_idle(self, cx, cy):
        """Breathing green orb with subtle pulse."""
        t = self._frame * 0.04
        # Gentle breathing: radius oscillates between 8 and 12
        breath = math.sin(t) * 0.5 + 0.5  # 0..1
        r = 8 + breath * 4

        # Outer glow (faint)
        glow_r = r + 3 + breath * 2
        self.canvas.create_oval(
            cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r,
            fill="", outline="#22c55e", width=1
        )

        # Core orb
        self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            fill="#22c55e", outline="#16a34a", width=2
        )

        # Inner highlight
        hr = r * 0.4
        self.canvas.create_oval(
            cx - hr - 1, cy - hr - 2, cx + hr - 1, cy + hr - 2,
            fill="#4ade80", outline=""
        )

    def _draw_recording(self, cx, cy, volume):
        """Pulsing red orb with expanding ripple rings based on voice volume."""
        t = self._frame * 0.08
        scaled_vol = min(volume * 5, 1.0)

        # Ripple rings (expanding outward from center)
        for i in range(3):
            phase = (t + i * 0.7) % 3.0
            ring_r = 10 + phase * 12 + scaled_vol * 8
            alpha_factor = max(0, 1.0 - phase / 3.0)
            width = max(1, int(3 * alpha_factor))
            # Color fades as ring expands
            red_val = int(239 * alpha_factor)
            color = f"#{red_val:02x}4444" if red_val > 15 else "#1a1111"
            self.canvas.create_oval(
                cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r,
                fill="", outline=color, width=width
            )

        # Core orb (size reacts to volume)
        core_r = 8 + scaled_vol * 6
        self.canvas.create_oval(
            cx - core_r, cy - core_r, cx + core_r, cy + core_r,
            fill="#ef4444", outline="#b91c1c", width=2
        )

        # Bright center dot
        dot_r = 3 + scaled_vol * 2
        self.canvas.create_oval(
            cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r,
            fill="#fca5a5", outline=""
        )

    def _draw_processing(self, cx, cy):
        """Spinning amber indicator."""
        t = self._frame * 0.1
        r = 10

        # Background circle
        self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            fill="#f59e0b", outline="#d97706", width=2
        )

        # Spinning dot
        dot_x = cx + math.cos(t) * (r - 3)
        dot_y = cy + math.sin(t) * (r - 3)
        self.canvas.create_oval(
            dot_x - 2, dot_y - 2, dot_x + 2, dot_y + 2,
            fill="#fef3c7", outline=""
        )

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = FloatingOrb()
    app.run()
