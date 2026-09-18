"""
DrowsApp Master Suite - Integrated Dashboard Application.

Integrates:
1. Drowsiness & Fatigue Detector (MediaPipe + OpenCV).
2. Drawing & Creative Canvas Studio (Pillow + Tkinter).
3. Interactive 4D Tesseract Explorer (Perspective Hypercube Renderer).
4. Guardian Split-Mode (Simultaneous Drawing & Fatigue Monitoring).
"""

import sys
import tkinter as tk
from tkinter import messagebox, ttk

from modules.canvas_view import CanvasView
from modules.drowsiness_engine import DrowsinessEngine
from modules.monitor_view import MonitorView
from modules.tesseract_view import TesseractView


class MasterDashboard(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("DrowsApp Studio - Creative & Fatigue Analytics Suite")
        self.geometry("1280x840")
        self.minsize(1000, 700)
        self.configure(bg="#0E131A")

        # Global Drowsiness Engine
        self.engine = DrowsinessEngine(ear_threshold=0.24, frame_limit=25, alarm_enabled=True)
        self.engine.on_drowsiness_callback = self._on_drowsiness_event
        self.engine.start()

        self._setup_styles()
        self._build_layout()
        self._poll_guardian_status()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

    def _build_layout(self):
        # 1. Global Alert Banner (Guardian Banner)
        self.banner = tk.Frame(self, bg="#1B263B", height=36)
        self.banner.pack(side=tk.TOP, fill=tk.X)

        self.lbl_banner_title = tk.Label(
            self.banner, text="🛡️ GUARDIAN STATUS: ACTIVE",
            font=("Segoe UI", 10, "bold"), fg="#00E5FF", bg="#1B263B", padx=15, pady=6
        )
        self.lbl_banner_title.pack(side=tk.LEFT)

        self.lbl_banner_ear = tk.Label(
            self.banner, text="Live EAR: 0.00 | Fatigue Incidents: 0",
            font=("Segoe UI", 9), fg="#94A3B8", bg="#1B263B", padx=10
        )
        self.lbl_banner_ear.pack(side=tk.LEFT)

        self.lbl_alert_box = tk.Label(
            self.banner, text="Status: Awake & Focused",
            font=("Segoe UI", 9, "bold"), fg="#10B981", bg="#1B263B", padx=15
        )
        self.lbl_alert_box.pack(side=tk.RIGHT)

        # 2. Main Body (Sidebar + Content Area)
        body = tk.Frame(self, bg="#0E131A")
        body.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        sidebar = tk.Frame(body, bg="#161F2E", width=220)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # App Brand Header
        brand_frame = tk.Frame(sidebar, bg="#161F2E", pady=18, padx=12)
        brand_frame.pack(fill=tk.X)
        tk.Label(brand_frame, text="DrowsApp", font=("Segoe UI", 16, "bold"), fg="#00E5FF", bg="#161F2E").pack(anchor=tk.W)
        tk.Label(brand_frame, text="Creative & Vision Suite", font=("Segoe UI", 9), fg="#64748B", bg="#161F2E").pack(anchor=tk.W)

        tk.Frame(sidebar, height=1, bg="#243447").pack(fill=tk.X, padx=10, pady=(0, 10))

        # Nav Buttons
        self.nav_buttons = {}
        nav_items = [
            ("🎨  Drawing Studio", "canvas"),
            ("👁️  Fatigue Monitor", "monitor"),
            ("🌌  4D Tesseract", "tesseract"),
            ("🛡️  Split Guardian", "split"),
        ]

        for text, key in nav_items:
            btn = tk.Button(
                sidebar, text=text, font=("Segoe UI", 11),
                fg="#E2E8F0", bg="#161F2E", activebackground="#00B4D8", activeforeground="#FFFFFF",
                relief=tk.FLAT, anchor=tk.W, padx=16, pady=10,
                command=lambda k=key: self.show_view(k)
            )
            btn.pack(fill=tk.X, padx=8, pady=3)
            self.nav_buttons[key] = btn

        # Bottom info card in sidebar
        side_footer = tk.Frame(sidebar, bg="#111827", pady=12, padx=10)
        side_footer.pack(side=tk.BOTTOM, fill=tk.X)
        tk.Label(side_footer, text="Webcam Guardian: ON", font=("Segoe UI", 8, "bold"), fg="#10B981", bg="#111827").pack(anchor=tk.W)
        tk.Label(side_footer, text="Background EAR tracking", font=("Segoe UI", 8), fg="#64748B", bg="#111827").pack(anchor=tk.W)

        # 3. Dynamic Content Container
        self.container = tk.Frame(body, bg="#0E131A")
        self.container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Initialize Views
        self.views = {
            "canvas": CanvasView(self.container),
            "monitor": MonitorView(self.container, self.engine),
            "tesseract": TesseractView(self.container),
            "split": self._create_split_view()
        }

        # Show initial view
        self.show_view("canvas")

    def _create_split_view(self):
        split_frame = tk.Frame(self.container, bg="#0E131A")

        # Left: Drawing Canvas
        left_box = tk.LabelFrame(split_frame, text=" Drawing Studio ", font=("Segoe UI", 10, "bold"), fg="#94A3B8", bg="#161F2E", bd=1)
        left_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 2), pady=4)
        canvas_sub = CanvasView(left_box)
        canvas_sub.pack(fill=tk.BOTH, expand=True)

        # Right: 4D Tesseract Visualizer
        right_box = tk.LabelFrame(split_frame, text=" 4D Tesseract Companion ", font=("Segoe UI", 10, "bold"), fg="#94A3B8", bg="#161F2E", bd=1)
        right_box.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(2, 4), pady=4)
        tesseract_sub = TesseractView(right_box)
        tesseract_sub.pack(fill=tk.BOTH, expand=True)

        return split_frame

    def show_view(self, key):
        # Hide all views
        for v in self.views.values():
            v.pack_forget()

        # Update button highlights
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.config(bg="#0077B6", fg="#FFFFFF", font=("Segoe UI", 11, "bold"))
            else:
                btn.config(bg="#161F2E", fg="#E2E8F0", font=("Segoe UI", 11))

        # Show selected view
        self.views[key].pack(fill=tk.BOTH, expand=True)

    def _on_drowsiness_event(self, is_drowsy):
        # Callback triggered from background engine thread
        pass

    def _poll_guardian_status(self):
        snap = self.engine.get_snapshot()
        ear = snap["ear"]
        is_drowsy = snap["is_drowsy"]
        closed = snap["closed_frames"]
        events = snap["event_count"]

        self.lbl_banner_ear.config(text=f"Live EAR: {ear:.3f} | Fatigue Incidents: {events}")

        if is_drowsy:
            self.banner.config(bg="#7F1D1D")
            self.lbl_banner_title.config(bg="#7F1D1D", text="⚠️ GUARDIAN ALERT: DROWSINESS DETECTED!")
            self.lbl_banner_ear.config(bg="#7F1D1D", fg="#FCA5A5")
            self.lbl_alert_box.config(bg="#7F1D1D", text="⚠️ WAKE UP / TAKE A BREAK", fg="#FEE2E2")
        elif closed > 5:
            self.banner.config(bg="#78350F")
            self.lbl_banner_title.config(bg="#78350F", text="⚠️ GUARDIAN WARNING: EYES CLOSING")
            self.lbl_banner_ear.config(bg="#78350F", fg="#FDE68A")
            self.lbl_alert_box.config(bg="#78350F", text="Eyes Closing...", fg="#FEF3C7")
        else:
            self.banner.config(bg="#1B263B")
            self.lbl_banner_title.config(bg="#1B263B", text="🛡️ GUARDIAN STATUS: ACTIVE")
            self.lbl_banner_ear.config(bg="#1B263B", fg="#94A3B8")
            self.lbl_alert_box.config(bg="#1B263B", text="Status: Awake & Focused", fg="#10B981")

        self.after(50, self._poll_guardian_status)

    def _on_close(self):
        self.engine.stop()
        self.destroy()
        sys.exit(0)


def main():
    app = MasterDashboard()
    app.mainloop()


if __name__ == "__main__":
    main()
