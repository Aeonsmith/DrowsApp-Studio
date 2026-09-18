"""
Embedded 4D Tesseract Visualizer View for DrowsApp Suite.
Runs seamlessly inside the Tkinter Dashboard without external window dependencies.
"""

import math
import tkinter as tk
from tkinter import ttk
import numpy as np
from PIL import Image, ImageDraw, ImageTk


# 16 vertices of 4D Hypercube (±1, ±1, ±1, ±1)
VERTICES_4D = np.array([
    [x, y, z, w]
    for x in (-1.0, 1.0)
    for y in (-1.0, 1.0)
    for z in (-1.0, 1.0)
    for w in (-1.0, 1.0)
], dtype=np.float32)

# 32 Edges
EDGES = []
for i in range(16):
    for j in range(i + 1, 16):
        if np.sum(VERTICES_4D[i] != VERTICES_4D[j]) == 1:
            EDGES.append((i, j))

# 24 Square Faces
FACES = []
for dim1 in range(4):
    for dim2 in range(dim1 + 1, 4):
        fixed_dims = [d for d in range(4) if d not in (dim1, dim2)]
        for val1 in (-1.0, 1.0):
            for val2 in (-1.0, 1.0):
                face = []
                for idx, v in enumerate(VERTICES_4D):
                    if v[fixed_dims[0]] == val1 and v[fixed_dims[1]] == val2:
                        face.append(idx)
                if len(face) == 4:
                    coords = [VERTICES_4D[idx][[dim1, dim2]] for idx in face]
                    angles = [math.atan2(c[1], c[0]) for c in coords]
                    face = [x for _, x in sorted(zip(angles, face))]
                    FACES.append(face)


class TesseractView(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, bg="#0F141C", *args, **kwargs)

        self.angles = {
            "XY": 0.0, "XZ": 0.0, "XW": 0.0,
            "YZ": 0.0, "YW": 0.0, "ZW": 0.0
        }
        self.speeds = {
            "XY": 0.008, "XZ": 0.000, "XW": 0.015,
            "YZ": 0.000, "YW": 0.012, "ZW": 0.018
        }
        self.active_planes = {
            "XY": True, "XZ": False, "XW": True,
            "YZ": False, "YW": True, "ZW": True
        }

        self.dist_4d = 2.8
        self.dist_3d = 3.5
        self.scale = 320.0
        self.paused = False

        self.show_faces = True
        self.show_edges = True
        self.show_vertices = True

        self.mouse_dragging = False
        self.last_x = 0
        self.last_y = 0
        self._tk_img = None

        self._build_ui()
        self._animate()

    def _build_ui(self):
        # Control Header Toolbar
        toolbar = tk.Frame(self, bg="#1A222D", pady=6, padx=10)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        tk.Label(toolbar, text="4D Hypercube Controls:", fg="#00E5FF", bg="#1A222D", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))

        # 6-Plane Toggles
        self.plane_buttons = {}
        for p in ["XY", "XZ", "XW", "YZ", "YW", "ZW"]:
            active = self.active_planes[p]
            btn = tk.Button(
                toolbar, text=p, font=("Segoe UI", 9, "bold"),
                bg="#00B4D8" if active else "#2D3748", fg="#FFFFFF",
                relief=tk.FLAT, padx=6, pady=2,
                command=lambda pl=p: self.toggle_plane(pl)
            )
            btn.pack(side=tk.LEFT, padx=2)
            self.plane_buttons[p] = btn

        tk.Frame(toolbar, width=2, height=24, bg="#4A5568").pack(side=tk.LEFT, padx=8)

        # Pause / Play
        self.btn_pause = tk.Button(toolbar, text="Pause", font=("Segoe UI", 9), bg="#3182CE", fg="#FFFFFF", relief=tk.FLAT, padx=8, pady=2, command=self.toggle_pause)
        self.btn_pause.pack(side=tk.LEFT, padx=3)

        # Reset
        btn_reset = tk.Button(toolbar, text="Reset View", font=("Segoe UI", 9), bg="#4A5568", fg="#FFFFFF", relief=tk.FLAT, padx=8, pady=2, command=self.reset_view)
        btn_reset.pack(side=tk.LEFT, padx=3)

        # Feature Toggles
        self.var_faces = tk.BooleanVar(value=self.show_faces)
        chk_f = tk.Checkbutton(toolbar, text="Faces", variable=self.var_faces, bg="#1A222D", fg="#E2E8F0", selectcolor="#2D3748", activebackground="#1A222D", command=self._update_render_options)
        chk_f.pack(side=tk.LEFT, padx=5)

        self.var_verts = tk.BooleanVar(value=self.show_vertices)
        chk_v = tk.Checkbutton(toolbar, text="Vertices", variable=self.var_verts, bg="#1A222D", fg="#E2E8F0", selectcolor="#2D3748", activebackground="#1A222D", command=self._update_render_options)
        chk_v.pack(side=tk.LEFT, padx=5)

        # Zoom Slider
        tk.Label(toolbar, text="Zoom:", fg="#E2E8F0", bg="#1A222D", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(8, 2))
        self.scale_slider = tk.Scale(
            toolbar, from_=100, to=700, orient=tk.HORIZONTAL,
            bg="#1A222D", fg="#E2E8F0", highlightthickness=0,
            troughcolor="#2D3748", length=110,
            command=self._on_scale_change
        )
        self.scale_slider.set(self.scale)
        self.scale_slider.pack(side=tk.LEFT, padx=2)

        # Canvas Display Area
        self.canvas = tk.Canvas(self, bg="#0A0E17", highlightthickness=0, cursor="fleur")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Mouse Bindings
        self.canvas.bind("<Button-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)

    def toggle_plane(self, p):
        self.active_planes[p] = not self.active_planes[p]
        self.plane_buttons[p].config(bg="#00B4D8" if self.active_planes[p] else "#2D3748")

    def toggle_pause(self):
        self.paused = not self.paused
        self.btn_pause.config(text="Resume" if self.paused else "Pause", bg="#38A169" if self.paused else "#3182CE")

    def reset_view(self):
        for p in self.angles:
            self.angles[p] = 0.0
        self.scale = 320.0
        self.scale_slider.set(self.scale)

    def _update_render_options(self):
        self.show_faces = self.var_faces.get()
        self.show_vertices = self.var_verts.get()

    def _on_scale_change(self, val):
        self.scale = float(val)

    def _on_mouse_down(self, event):
        self.last_x = event.x
        self.last_y = event.y

    def _on_mouse_drag(self, event):
        dx = event.x - self.last_x
        dy = event.y - self.last_y
        self.angles["XZ"] += dx * 0.008
        self.angles["YZ"] += dy * 0.008
        self.last_x = event.x
        self.last_y = event.y

    def _on_mouse_wheel(self, event):
        if event.delta > 0:
            self.scale = min(700.0, self.scale * 1.08)
        else:
            self.scale = max(100.0, self.scale / 1.08)
        self.scale_slider.set(self.scale)

    def _get_rotation_matrix(self):
        R = np.eye(4, dtype=np.float32)
        def rot_plane(i, j, theta):
            M = np.eye(4, dtype=np.float32)
            c, s = np.cos(theta), np.sin(theta)
            M[i, i], M[i, j] = c, -s
            M[j, i], M[j, j] = s, c
            return M

        if self.angles["XY"] != 0: R = R @ rot_plane(0, 1, self.angles["XY"])
        if self.angles["XZ"] != 0: R = R @ rot_plane(0, 2, self.angles["XZ"])
        if self.angles["XW"] != 0: R = R @ rot_plane(0, 3, self.angles["XW"])
        if self.angles["YZ"] != 0: R = R @ rot_plane(1, 2, self.angles["YZ"])
        if self.angles["YW"] != 0: R = R @ rot_plane(1, 3, self.angles["YW"])
        if self.angles["ZW"] != 0: R = R @ rot_plane(2, 3, self.angles["ZW"])
        return R

    def _project(self, vertices, w_canvas, h_canvas):
        projected_2d = []
        depths_3d = []
        w_vals = []
        cx, cy = w_canvas / 2.0, h_canvas / 2.0

        for v in vertices:
            x, y, z, w = v
            w_vals.append(w)
            denom_4d = max(0.1, self.dist_4d - w)
            w_s = 1.0 / denom_4d
            x3, y3, z3 = x * w_s, y * w_s, z * w_s
            depths_3d.append(z3)

            denom_3d = max(0.1, self.dist_3d - z3)
            z_s = 1.0 / denom_3d
            sx = cx + x3 * z_s * self.scale
            sy = cy - y3 * z_s * self.scale
            projected_2d.append((sx, sy))

        return projected_2d, depths_3d, w_vals

    def _animate(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        if w > 50 and h > 50:
            if not self.paused:
                for p in self.active_planes:
                    if self.active_planes[p]:
                        self.angles[p] = (self.angles[p] + self.speeds[p]) % (2 * math.pi)

            # Transform & Project
            rot_matrix = self._get_rotation_matrix()
            transformed = VERTICES_4D @ rot_matrix.T
            proj_2d, depths_3d, w_vals = self._project(transformed, w, h)

            # Create PIL image for anti-aliased & alpha-blended rendering
            img = Image.new("RGBA", (w, h), (10, 14, 23, 255))
            draw = ImageDraw.Draw(img)

            # 1. Render Transparent Faces
            if self.show_faces:
                face_depths = []
                for face in FACES:
                    avg_z = np.mean([depths_3d[i] for i in face])
                    avg_w = np.mean([w_vals[i] for i in face])
                    face_depths.append((avg_z, avg_w, face))

                face_depths.sort(key=lambda item: item[0], reverse=False)
                for avg_z, avg_w, face in face_depths:
                    poly = [proj_2d[idx] for idx in face]
                    t = (avg_w + 1.0) / 2.0
                    r = int(30 + t * 180)
                    g = int(20 + (1 - t) * 140)
                    b = int(220 + (1 - t) * 35)
                    # Semi-transparent face
                    draw.polygon(poly, fill=(r, g, b, 45))

            # 2. Render 32 Glowing Edges
            if self.show_edges:
                for i, j in EDGES:
                    p1 = proj_2d[i]
                    p2 = proj_2d[j]
                    avg_w = (w_vals[i] + w_vals[j]) / 2.0
                    t = (avg_w + 1.0) / 2.0
                    r = int(0 + t * 255)
                    g = int(220 - t * 100)
                    b = int(255 - t * 40)
                    draw.line([p1, p2], fill=(r, g, b, 240), width=2)

            # 3. Render 16 Vertices
            if self.show_vertices:
                for i, pt in enumerate(proj_2d):
                    w_val = w_vals[i]
                    radius = 4 + (w_val + 1.0) * 1.5
                    draw.ellipse([pt[0] - radius, pt[1] - radius, pt[0] + radius, pt[1] + radius], fill=(0, 255, 200, 255), outline=(255, 255, 255, 255))

            # Render to Tkinter Canvas
            self._tk_img = ImageTk.PhotoImage(img)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self._tk_img)

        self.after(25, self._animate)
