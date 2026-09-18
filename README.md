# DrowsApp Studio — Creative & Vision Analytics Suite

**DrowsApp Studio** is an integrated desktop dashboard application combining real-time computer vision drowsiness monitoring, a full-featured creative drawing canvas, and an interactive 4D tesseract (hypercube) projection engine.

---

## 🌟 Key Features

### 1. 🎨 Creative Drawing Studio
- **Tools**: Pen, Brush, Eraser, Line, Rectangle, and Oval/Circle shapes.
- **Color & Sizing**: Full RGB color chooser dialog, quick preset palette, and dynamic brush size slider.
- **History & Export**: 30-step Undo/Redo stack with lossless Pillow image backing and PNG/JPEG/BMP file export.
- **Shortcuts**: `Ctrl+Z` (Undo), `Ctrl+Y` (Redo), `Ctrl+S` (Save), `Ctrl+N` (Clear).

### 2. 👁️ Real-Time Drowsiness & Fatigue Monitor
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
- **Split Workspace**: Allows drawing or manipulating the 4D hypercube side-by-side.

---

## 📁 Project Structure

```text
drowsapp_suite/
├── requirements.txt            # Project dependencies
├── main.py                     # Master Dashboard entry point
├── README.md                   # Documentation and usage guide
└── modules/
    ├── __init__.py
    ├── canvas_view.py          # Drawing canvas component
    ├── drowsiness_engine.py    # Threaded OpenCV/MediaPipe detection engine
    ├── monitor_view.py         # Fatigue telemetry HUD and camera controls
    └── tesseract_view.py       # Embedded 4D tesseract canvas renderer
```

---

## 🚀 Installation & Prerequisites

### Prerequisites
- **Python**: Version 3.9, 3.10, or 3.11+
- **Hardware**: Standard webcam for eye tracking (optional for drawing/tesseract modes)
- **OS**: Windows (native `winsound` supported), macOS, or Linux

### 1. Clone or Navigate to Project Directory
```powershell
cd drowsapp_suite
```

### 2. Set Up a Virtual Environment (Recommended)
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 🎮 Running the Application

Launch the unified suite:
```powershell
python main.py
```

---

## 📖 Usage Guide

### Sidebar Navigation
Use the left sidebar to navigate between views:
- **🎨 Drawing Studio**: Access the digital whiteboard and canvas studio.
- **👁️ Fatigue Monitor**: Inspect live video feed, calibrate sensitivity, and view telemetry metrics.
- **🌌 4D Tesseract**: Explore the 4-dimensional hypercube and toggle rotation planes.
- **🛡️ Split Guardian**: Work in a side-by-side workspace with active fatigue alerts.

### Calibrating Fatigue Sensitivity
1. Open the **Fatigue Monitor** tab.
2. Watch the **Live EAR** meter with your eyes open (typical values: `0.28` – `0.38`).
3. Close your eyes and observe the drop in EAR (typical closed values: `0.10` – `0.20`).
4. Set the **EAR Threshold** slider slightly above your closed-eye baseline (e.g., `0.22` – `0.26`).
5. Adjust **Frame Duration Threshold** to control how many frames eyes must remain closed before triggering the alarm.

---

## ⌨️ Keyboard & Mouse Shortcuts

| Context | Action | Shortcut / Control |
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

## 📄 License
This project is open-source and available under the MIT License.
