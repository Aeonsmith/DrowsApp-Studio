"""
Canvas View Component for DrowsApp Suite.
"""

import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageTk


class CanvasView(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.current_tool = "pen"
        self.primary_color = "#1E1E1E"
        self.bg_color = "#FFFFFF"
        self.brush_size = 4
        self.start_x = None
        self.start_y = None
        self.temp_shape_id = None

        self.canvas_width = 1600
        self.canvas_height = 1200

        self.image = Image.new("RGB", (self.canvas_width, self.canvas_height), self.bg_color)
        self.draw = ImageDraw.Draw(self.image)

        self.undo_stack = [self.image.copy()]
        self.redo_stack = []
        self.max_history = 30

        self._build_ui()

    def _build_ui(self):
        # Toolbar
        toolbar = tk.Frame(self, bg="#2C3E50", pady=6, padx=8)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        tk.Label(toolbar, text="Tools:", fg="#ECF0F1", bg="#2C3E50", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(5, 3))

        self.tool_buttons = {}
        tools = [
            ("Pen", "pen"),
            ("Brush", "brush"),
            ("Eraser", "eraser"),
            ("Line", "line"),
            ("Rectangle", "rectangle"),
            ("Oval", "oval"),
        ]
        for label, mode in tools:
            btn = tk.Button(
                toolbar, text=label, font=("Segoe UI", 9),
                bg="#34495E" if mode != self.current_tool else "#1ABC9C",
                fg="#FFFFFF", relief=tk.FLAT, padx=8, pady=3,
                command=lambda m=mode: self.set_tool(m)
            )
            btn.pack(side=tk.LEFT, padx=2)
            self.tool_buttons[mode] = btn

        tk.Frame(toolbar, width=2, height=26, bg="#7F8C8D").pack(side=tk.LEFT, padx=10)

        tk.Label(toolbar, text="Size:", fg="#ECF0F1", bg="#2C3E50", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.size_scale = tk.Scale(
            toolbar, from_=1, to=50, orient=tk.HORIZONTAL,
            bg="#2C3E50", fg="#ECF0F1", highlightthickness=0,
            troughcolor="#34495E", activebackground="#1ABC9C",
            command=self._on_size_change, length=110
        )
        self.size_scale.set(self.brush_size)
        self.size_scale.pack(side=tk.LEFT, padx=2)

        tk.Frame(toolbar, width=2, height=26, bg="#7F8C8D").pack(side=tk.LEFT, padx=10)

        tk.Label(toolbar, text="Color:", fg="#ECF0F1", bg="#2C3E50", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.color_preview = tk.Label(toolbar, bg=self.primary_color, width=3, height=1, relief=tk.SOLID, bd=1)
        self.color_preview.pack(side=tk.LEFT, padx=3)

        btn_color = tk.Button(
            toolbar, text="Pick Color", font=("Segoe UI", 9),
            bg="#34495E", fg="#FFFFFF", relief=tk.FLAT, padx=6, pady=3,
            command=self.choose_color
        )
        btn_color.pack(side=tk.LEFT, padx=2)

        # Palette
        pal_frame = tk.Frame(toolbar, bg="#2C3E50")
        pal_frame.pack(side=tk.LEFT, padx=8)
        preset_colors = ["#1E1E1E", "#E74C3C", "#E67E22", "#F1C40F", "#2ECC71", "#3498DB", "#9B59B6", "#FFFFFF"]
        for col in preset_colors:
            p_btn = tk.Button(
                pal_frame, bg=col, width=2, height=1, relief=tk.GROOVE, bd=1,
                command=lambda c=col: self.set_color(c)
            )
            p_btn.pack(side=tk.LEFT, padx=1)

        # Actions
        btn_save = tk.Button(toolbar, text="Save / Export", font=("Segoe UI", 9, "bold"), bg="#27AE60", fg="#FFFFFF", relief=tk.FLAT, padx=10, pady=3, command=self.save_image)
        btn_save.pack(side=tk.RIGHT, padx=5)

        btn_clear = tk.Button(toolbar, text="Clear", font=("Segoe UI", 9), bg="#C0392B", fg="#FFFFFF", relief=tk.FLAT, padx=8, pady=3, command=self.clear_canvas)
        btn_clear.pack(side=tk.RIGHT, padx=3)

        btn_redo = tk.Button(toolbar, text="Redo", font=("Segoe UI", 9), bg="#34495E", fg="#FFFFFF", relief=tk.FLAT, padx=8, pady=3, command=self.redo)
        btn_redo.pack(side=tk.RIGHT, padx=3)

        btn_undo = tk.Button(toolbar, text="Undo", font=("Segoe UI", 9), bg="#34495E", fg="#FFFFFF", relief=tk.FLAT, padx=8, pady=3, command=self.undo)
        btn_undo.pack(side=tk.RIGHT, padx=3)

        # Canvas Area
        canvas_container = tk.Frame(self, bg="#BDC3C7")
        canvas_container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            canvas_container, bg=self.bg_color,
            width=self.canvas_width, height=self.canvas_height,
            scrollregion=(0, 0, self.canvas_width, self.canvas_height),
            cursor="crosshair"
        )

        h_scroll = tk.Scrollbar(canvas_container, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scroll = tk.Scrollbar(canvas_container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Mouse Events
        self.canvas.bind("<Button-1>", self._on_button_press)
        self.canvas.bind("<B1-Motion>", self._on_paint_motion)
        self.canvas.bind("<ButtonRelease-1>", self._on_button_release)

    def set_tool(self, tool_name):
        self.current_tool = tool_name
        for name, btn in self.tool_buttons.items():
            btn.config(bg="#1ABC9C" if name == tool_name else "#34495E")

    def set_color(self, hex_color):
        self.primary_color = hex_color
        self.color_preview.config(bg=hex_color)
        if self.current_tool == "eraser":
            self.set_tool("pen")

    def choose_color(self):
        color_code = colorchooser.askcolor(title="Choose Brush Color", initialcolor=self.primary_color)
        if color_code and color_code[1]:
            self.set_color(color_code[1])

    def _on_size_change(self, val):
        self.brush_size = int(val)

    def _on_button_press(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.start_x = x
        self.start_y = y
        self.last_x = x
        self.last_y = y

        if self.current_tool in ("pen", "brush", "eraser"):
            color = self.bg_color if self.current_tool == "eraser" else self.primary_color
            size = self.brush_size * 2 if self.current_tool == "brush" else (self.brush_size * 3 if self.current_tool == "eraser" else self.brush_size)
            r = size / 2.0
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline=color)
            self.draw.ellipse([x - r, y - r, x + r, y + r], fill=color, outline=color)

    def _on_paint_motion(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        if self.current_tool in ("pen", "brush", "eraser"):
            color = self.bg_color if self.current_tool == "eraser" else self.primary_color
            size = self.brush_size * 2 if self.current_tool == "brush" else (self.brush_size * 3 if self.current_tool == "eraser" else self.brush_size)

            self.canvas.create_line(
                self.last_x, self.last_y, x, y,
                width=size, fill=color, capstyle=tk.ROUND, smooth=True, splinesteps=36
            )
            self.draw.line([self.last_x, self.last_y, x, y], fill=color, width=size, joint="curve")
            r = size / 2.0
            self.draw.ellipse([x - r, y - r, x + r, y + r], fill=color, outline=color)

            self.last_x = x
            self.last_y = y

        elif self.current_tool in ("line", "rectangle", "oval"):
            if self.temp_shape_id:
                self.canvas.delete(self.temp_shape_id)

            color = self.primary_color
            if self.current_tool == "line":
                self.temp_shape_id = self.canvas.create_line(self.start_x, self.start_y, x, y, width=self.brush_size, fill=color, capstyle=tk.ROUND)
            elif self.current_tool == "rectangle":
                self.temp_shape_id = self.canvas.create_rectangle(self.start_x, self.start_y, x, y, outline=color, width=self.brush_size)
            elif self.current_tool == "oval":
                self.temp_shape_id = self.canvas.create_oval(self.start_x, self.start_y, x, y, outline=color, width=self.brush_size)

    def _on_button_release(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        color = self.primary_color
        if self.current_tool == "line":
            self.draw.line([self.start_x, self.start_y, x, y], fill=color, width=self.brush_size)
        elif self.current_tool == "rectangle":
            self.draw.rectangle([min(self.start_x, x), min(self.start_y, y), max(self.start_x, x), max(self.start_y, y)], outline=color, width=self.brush_size)
        elif self.current_tool == "oval":
            self.draw.ellipse([min(self.start_x, x), min(self.start_y, y), max(self.start_x, x), max(self.start_y, y)], outline=color, width=self.brush_size)

        self.temp_shape_id = None
        self._push_undo()

    def _push_undo(self):
        self.undo_stack.append(self.image.copy())
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def undo(self):
        if len(self.undo_stack) > 1:
            self.redo_stack.append(self.undo_stack.pop())
            self.image = self.undo_stack[-1].copy()
            self.draw = ImageDraw.Draw(self.image)
            self._redraw_canvas()

    def redo(self):
        if self.redo_stack:
            restored = self.redo_stack.pop()
            self.undo_stack.append(restored.copy())
            self.image = restored.copy()
            self.draw = ImageDraw.Draw(self.image)
            self._redraw_canvas()

    def _redraw_canvas(self):
        self._tk_img = ImageTk.PhotoImage(self.image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self._tk_img)

    def clear_canvas(self):
        if messagebox.askyesno("Clear Canvas", "Clear canvas artwork?"):
            self.canvas.delete("all")
            self.image = Image.new("RGB", (self.canvas_width, self.canvas_height), self.bg_color)
            self.draw = ImageDraw.Draw(self.image)
            self._push_undo()

    def save_image(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG image (*.png)", "*.png"), ("JPEG image (*.jpg)", "*.jpg"), ("All Files (*.*)", "*.*")],
            title="Save Canvas Artwork"
        )
        if file_path:
            try:
                self.image.save(file_path)
                messagebox.showinfo("Saved", f"File saved successfully:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save:\n{e}")
