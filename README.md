# DrowsApp Studio — Creative & Vision Analytics Suite

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Release](https://img.shields.io/github/v/release/Aeonsmith/DrowsApp-Studio)](https://github.com/Aeonsmith/DrowsApp-Studio/releases)

**DrowsApp Studio** is an integrated desktop application combining real-time computer vision eye fatigue monitoring, a high-resolution digital drawing canvas, and an interactive 4D tesseract (hypercube) projection visualizer into a unified workspace.

---

## 🌟 Key Features

### 1. 🎨 Creative Drawing Studio
- **Tools**: Pen, Brush, Eraser, Line, Rectangle, and Oval/Circle shapes.
- **Color & Sizing**: Full RGB color chooser dialog, quick preset palette, and dynamic brush size slider.
- **History & Export**: 30-step Undo/Redo stack with lossless Pillow image backing and PNG/JPEG/BMP file export.
- **Shortcuts**: `Ctrl+Z` (Undo), `Ctrl+Y` (Redo), `Ctrl+S` (Save), `Ctrl+N` (Clear).

### 2. 👁️ Real-Time Drowsiness & Fatigue Guardian
- **Facial Landmark Telemetry**: Uses MediaPipe Face Mesh and OpenCV to calculate real-time Eye Aspect Ratio (EAR).
- **Fatigue Detection**: Tracks consecutive closed-eye frames and alerts the user before micro-sleep occurs.
- **Audible & Visual Alarms**: Non-blocking audio alarm via Windows `winsound` / system chime and on-screen HUD alerts.
- **Customizable Sensitivity**: Real-time sliders to calibrate EAR thresholds (default: `0.24`) and duration limits (default: `25` frames).

### 3. 🌌 Interactive 4D Tesseract Explorer
- **True 4D Euclidean Geometry**: 16 vertices, 32 edges, and 24 square faces in $\mathbb{R}^4$.
- **Dual Perspective Projection**: Real-time 4D $\rightarrow$ 3D $\rightarrow$ 2D rendering.
- **6-Plane Rotation Engine**: Independent toggle controls for $XY, XZ, XW, YZ, YW,$ and $ZW$ rotation planes.
- **Interactive Manipulation**: Left-click and drag to orbit in view space; mouse scroll wheel to zoom.
- **Depth Cues**: Dynamic neon cyan-to-magenta gradient based on 4D $W$-depth and semi-transparent alpha polygons.

### 4. 🛡️ Split Guardian Mode & Global Background Monitor
- **Background Guardian**: The fatigue detector runs continuously across all tabs in a background thread.
- **Global Alert Banner**: Displays live EAR scores, fatigue event counts, and warning banners across the application.
- **Split Workspace**: Allows drawing or manipulating the 4D hypercube side-by-side with live fatigue telemetry.

---

## 📁 Project Structure

```text
drowsapp_suite/
├── requirements.txt            # Project dependencies
├── main.py                     # Master Dashboard entry point
├── README.md                   # Documentation and usage guide
├── CONTRIBUTING.md             # Contribution guidelines
├── LICENSE                     # MIT License
└── modules/
    ├── __init__.py
    ├── canvas_view.py          # Drawing canvas component
    ├── drowsiness_engine.py    # Threaded OpenCV/MediaPipe detection engine
    ├── monitor_view.py         # Fatigue telemetry HUD and camera controls
    └── tesseract_view.py       # Embedded 4D tesseract canvas renderer
```

---

## 🚀 Installation

### Prerequisites
- **Python**: Version 3.9, 3.10, 3.11, or 3.12+
- **Webcam**: Standard USB or built-in webcam for eye tracking (optional for canvas/tesseract modes)
- **Operating System**: Windows (native `winsound` supported), macOS, or Linux

### 1. Clone the Repository
```powershell
git clone https://github.com/Aeonsmith/DrowsApp-Studio.git
cd DrowsApp-Studio
```

### 2. Set Up a Virtual Environment (Recommended)
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate virtual environment (macOS / Linux)
source venv/bin/activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 💡 Usage Examples

### Example 1: Launching the Full Dashboard Application
Run the master dashboard with all modules integrated:
```powershell
python main.py
```

---

### Example 2: Using the Drowsiness Engine Programmatically
You can embed the `DrowsinessEngine` in your own scripts or pipelines:

```python
import time
from modules.drowsiness_engine import DrowsinessEngine

# Callback for fatigue alerts
def on_drowsiness_alert(is_drowsy):
    if is_drowsy:
        print("[ALERT] User is showing signs of fatigue / closed eyes!")

# Initialize engine with custom thresholds
engine = DrowsinessEngine(
    ear_threshold=0.25,      # Trigger when EAR drops below 0.25
    frame_limit=20,          # After 20 consecutive closed frames
    alarm_enabled=True       # Enable audible alert chime
)
engine.on_drowsiness_callback = on_drowsiness_alert

# Start webcam capture in a non-blocking background thread
engine.start(camera_index=0)

try:
    for _ in range(10):
        time.sleep(1)
        telemetry = engine.get_snapshot()
        print(f"Current EAR: {telemetry['ear']:.3f} | Closed Frames: {telemetry['closed_frames']} | Drowsy: {telemetry['is_drowsy']}")
finally:
    engine.stop()
```

---

### Example 3: Embedding the 4D Tesseract Viewer in a Custom Tkinter App
You can integrate the `TesseractView` into any custom Tkinter interface:

```python
import tkinter as tk
from modules.tesseract_view import TesseractView

root = tk.Tk()
root.title("Standalone 4D Tesseract Explorer")
root.geometry("800x600")

# Instantiate and mount the 4D visualizer component
tesseract_widget = TesseractView(root)
tesseract_widget.pack(fill=tk.BOTH, expand=True)

root.mainloop()
```

---

### Example 4: Embedding the Drawing Canvas in a Custom GUI
```python
import tkinter as tk
from modules.canvas_view import CanvasView

root = tk.Tk()
root.title("Standalone Drawing Canvas")
root.geometry("900x650")

# Instantiate and mount the Canvas component
canvas_widget = CanvasView(root)
canvas_widget.pack(fill=tk.BOTH, expand=True)

root.mainloop()
```

---

## ⚙️ Sensitivity Calibration Guide

1. Open the **Fatigue Monitor** tab.
2. Watch the **Live EAR** meter with your eyes open (typical values: `0.28` – `0.38`).
3. Close your eyes and observe the drop in EAR (typical closed values: `0.10` – `0.20`).
4. Set the **EAR Threshold** slider slightly above your closed-eye baseline (recommended: `0.22` – `0.26`).
5. Adjust **Frame Duration Threshold** to control how many frames eyes must remain closed before triggering the alarm.

---

## ⌨️ Keyboard & Mouse Controls

| View | Action | Shortcut / Control |
| :--- | :--- | :--- |
| **Canvas** | Undo stroke | `Ctrl + Z` |
| **Canvas** | Redo stroke | `Ctrl + Y` |
| **Canvas** | Save image | `Ctrl + S` |
| **Canvas** | Clear canvas | `Ctrl + N` |
| **Tesseract** | Orbit / Rotate View | `Left Click + Drag` |
| **Tesseract** | Zoom in / out | `Mouse Scroll Wheel` |
| **Tesseract** | Toggle 4D Planes | Click plane buttons (`XY`, `XZ`, `XW`, `YZ`, `YW`, `ZW`) |
| **Tesseract** | Pause / Resume | Click `Pause` / `Resume` |

---

## 🔧 Troubleshooting

- **Webcam Not Found / Black Feed:**
  Ensure no other application is using the webcam. Verify that your camera index in `modules/drowsiness_engine.py` (`camera_index=0`) matches your connected device.
- **Audio Alarm Not Playing:**
  On Windows, `winsound.Beep` is used automatically. Ensure your system volume is unmuted. On non-Windows platforms, a fallback console chime is triggered.
- **Performance / Frame Rate:**
  The vision engine and 4D renderer run on decoupled background loops to prevent UI freezing. Reduce camera resolution or disable face polygons in the tesseract toolbar if running on low-spec hardware.

---

## 🤝 Contributing
Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for instructions on setting up your environment, code standards, and opening pull requests.

---

## 📄 License
This project is open-source and licensed under the [MIT License](LICENSE).
