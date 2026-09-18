"""
Fatigue & Drowsiness Monitor View Component.
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class MonitorView(tk.Frame):
    def __init__(self, parent, engine, *args, **kwargs):
        super().__init__(parent, bg="#1E272C", *args, **kwargs)
        self.engine = engine
        self._tk_video_img = None

        self._build_ui()
        self._poll_telemetry()

    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg="#263238", pady=10, padx=15)
        header.pack(fill=tk.X)
        tk.Label(header, text="Drowsiness & Fatigue Telemetry Monitor", font=("Segoe UI", 13, "bold"), fg="#ECEFF1", bg="#263238").pack(side=tk.LEFT)

        # Main content area: Left = Video, Right = Telemetry & Controls
        content = tk.Frame(self, bg="#1E272C", padx=15, pady=15)
        content.pack(fill=tk.BOTH, expand=True)

        # Video Frame
        video_box = tk.LabelFrame(content, text=" Live Camera Feed ", font=("Segoe UI", 10, "bold"), fg="#90A4AE", bg="#263238", bd=2)
        video_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.video_label = tk.Label(video_box, bg="#11171A", text="Camera Initializing / Off", fg="#78909C", font=("Segoe UI", 11))
        self.video_label.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Right Panel: Controls & Metrics
        right_panel = tk.Frame(content, bg="#1E272C", width=340)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        # Status HUD Card
        hud_card = tk.LabelFrame(right_panel, text=" Fatigue Status ", font=("Segoe UI", 10, "bold"), fg="#90A4AE", bg="#263238", bd=2, padx=12, pady=12)
        hud_card.pack(fill=tk.X, pady=(0, 12))

        self.lbl_status = tk.Label(hud_card, text="STATUS: NORMAL", font=("Segoe UI", 12, "bold"), fg="#2ECC71", bg="#263238")
        self.lbl_status.pack(anchor=tk.W, pady=2)

        self.lbl_ear = tk.Label(hud_card, text="Eye Aspect Ratio (EAR): 0.00", font=("Segoe UI", 10), fg="#ECEFF1", bg="#263238")
        self.lbl_ear.pack(anchor=tk.W, pady=2)

        # EAR Progress Bar Indicator
        self.ear_bar = ttk.Progressbar(hud_card, orient=tk.HORIZONTAL, length=280, mode='determinate', maximum=0.45)
        self.ear_bar.pack(fill=tk.X, pady=6)

        self.lbl_frames = tk.Label(hud_card, text="Closed Frame Count: 0", font=("Segoe UI", 10), fg="#ECEFF1", bg="#263238")
        self.lbl_frames.pack(anchor=tk.W, pady=2)

        self.lbl_events = tk.Label(hud_card, text="Total Drowsy Incidents: 0", font=("Segoe UI", 10), fg="#E67E22", bg="#263238")
        self.lbl_events.pack(anchor=tk.W, pady=2)

        # Configuration Card
        cfg_card = tk.LabelFrame(right_panel, text=" Sensitivity Settings ", font=("Segoe UI", 10, "bold"), fg="#90A4AE", bg="#263238", bd=2, padx=12, pady=12)
        cfg_card.pack(fill=tk.X, pady=(0, 12))

        tk.Label(cfg_card, text="EAR Threshold:", fg="#ECEFF1", bg="#263238", font=("Segoe UI", 9)).pack(anchor=tk.W)
        self.ear_slider = tk.Scale(
            cfg_card, from_=0.15, to=0.35, resolution=0.01, orient=tk.HORIZONTAL,
            bg="#263238", fg="#ECEFF1", highlightthickness=0, troughcolor="#37474F",
            command=self._on_ear_slider
        )
        self.ear_slider.set(self.engine.ear_threshold)
        self.ear_slider.pack(fill=tk.X, pady=(0, 8))

        tk.Label(cfg_card, text="Frame Duration Threshold:", fg="#ECEFF1", bg="#263238", font=("Segoe UI", 9)).pack(anchor=tk.W)
        self.frame_slider = tk.Scale(
            cfg_card, from_=10, to=60, resolution=1, orient=tk.HORIZONTAL,
            bg="#263238", fg="#ECEFF1", highlightthickness=0, troughcolor="#37474F",
            command=self._on_frame_slider
        )
        self.frame_slider.set(self.engine.frame_limit)
        self.frame_slider.pack(fill=tk.X, pady=(0, 8))

        # Alarm Toggle Checkbox
        self.alarm_var = tk.BooleanVar(value=self.engine.alarm_enabled)
        chk_alarm = tk.Checkbutton(
            cfg_card, text="Audible Alarm Enabled", variable=self.alarm_var,
            bg="#263238", fg="#ECEFF1", selectcolor="#37474F", activebackground="#263238",
            command=self._on_alarm_toggle
        )
        chk_alarm.pack(anchor=tk.W, pady=4)

        # Stream Actions
        btn_frame = tk.Frame(right_panel, bg="#1E272C")
        btn_frame.pack(fill=tk.X, pady=8)

        self.btn_toggle_cam = tk.Button(
            btn_frame, text="Stop Camera", font=("Segoe UI", 10, "bold"),
            bg="#E74C3C", fg="#FFFFFF", relief=tk.FLAT, pady=6,
            command=self.toggle_camera
        )
        self.btn_toggle_cam.pack(fill=tk.X)

    def _on_ear_slider(self, val):
        self.engine.ear_threshold = float(val)

    def _on_frame_slider(self, val):
        self.engine.frame_limit = int(val)

    def _on_alarm_toggle(self):
        self.engine.alarm_enabled = self.alarm_var.get()

    def toggle_camera(self):
        if self.engine.running:
            self.engine.stop()
            self.btn_toggle_cam.config(text="Start Camera", bg="#2ECC71")
            self.video_label.config(image="", text="Camera Paused / Stopped")
        else:
            self.engine.start()
            self.btn_toggle_cam.config(text="Stop Camera", bg="#E74C3C")

    def _poll_telemetry(self):
        snap = self.engine.get_snapshot()

        # Update telemetry labels
        ear = snap["ear"]
        closed = snap["closed_frames"]
        drowsy = snap["is_drowsy"]
        events = snap["event_count"]

        self.lbl_ear.config(text=f"Eye Aspect Ratio (EAR): {ear:.3f}")
        self.ear_bar['value'] = min(ear, 0.45)
        self.lbl_frames.config(text=f"Closed Frame Count: {closed} / {self.engine.frame_limit}")
        self.lbl_events.config(text=f"Total Drowsy Incidents: {events}")

        if drowsy:
            self.lbl_status.config(text="⚠️ DROWSINESS DETECTED!", fg="#E74C3C")
        elif closed > 5:
            self.lbl_status.config(text="⚠️ EYES CLOSING...", fg="#F39C12")
        else:
            self.lbl_status.config(text="✓ STATUS: AWAKE / NORMAL", fg="#2ECC71")

        # Update Live Video
        frame_img = snap["frame"]
        if frame_img and self.engine.running:
            # Resize image to fit nicely in the window
            w = self.video_label.winfo_width()
            h = self.video_label.winfo_height()
            if w > 50 and h > 50:
                frame_img = frame_img.resize((w, h), Image.Resampling.BILINEAR)
            self._tk_video_img = ImageTk.PhotoImage(frame_img)
            self.video_label.config(image=self._tk_video_img, text="")

        self.after(30, self._poll_telemetry)
