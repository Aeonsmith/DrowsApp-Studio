"""
Core Drowsiness Detection Engine.
Compatible with MediaPipe 1.0+ (FaceLandmarker Task API) and legacy mp.solutions.
Runs video capture and processing in a background thread and emits status/frames.
"""

import os
import threading
import time
import urllib.request
import cv2
import mediapipe as mp
import numpy as np
from PIL import Image

try:
    import winsound
    def trigger_beep():
        winsound.Beep(2200, 300)
except ImportError:
    def trigger_beep():
        print("\a", end="", flush=True)


MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
MODEL_FILENAME = "face_landmarker.task"


def ensure_model_exists():
    """Ensures the face_landmarker.task model file is present locally."""
    # Check in current dir and script module dir
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    possible_paths = [
        os.path.join(parent_dir, MODEL_FILENAME),
        os.path.join(script_dir, MODEL_FILENAME),
        os.path.join(os.getcwd(), MODEL_FILENAME)
    ]
    for p in possible_paths:
        if os.path.exists(p) and os.path.getsize(p) > 100000:
            return p

    target_path = os.path.join(parent_dir, MODEL_FILENAME)
    try:
        print("Downloading MediaPipe face landmarker model bundle...")
        urllib.request.urlretrieve(MODEL_URL, target_path)
        return target_path
    except Exception as e:
        print(f"Warning: Could not auto-download model bundle: {e}")
        return None


class DrowsinessEngine:
    LEFT_EYE = [33, 160, 158, 133, 153, 144]
    RIGHT_EYE = [362, 385, 387, 263, 373, 380]

    def __init__(self, ear_threshold=0.24, frame_limit=25, alarm_enabled=True):
        self.ear_threshold = ear_threshold
        self.frame_limit = frame_limit
        self.alarm_enabled = alarm_enabled

        self.running = False
        self.thread = None
        self.cap = None

        # Telemetry State
        self.current_ear = 0.0
        self.closed_frames = 0
        self.is_drowsy = False
        self.drowsy_event_count = 0
        self.last_alarm_time = 0
        self.latest_frame = None  # PIL.Image
        self.lock = threading.Lock()

        # Alert callback hook
        self.on_drowsiness_callback = None

    def start(self, camera_index=0):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, args=(camera_index,), daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.5)
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None

    def _calc_ear(self, landmarks, indices, w, h):
        pts = np.array([[landmarks[i].x * w, landmarks[i].y * h] for i in indices])
        v1 = np.linalg.norm(pts[1] - pts[5])
        v2 = np.linalg.norm(pts[2] - pts[4])
        horiz = np.linalg.norm(pts[0] - pts[3])
        if horiz == 0:
            return 0.0, pts.astype(np.int32)
        return (v1 + v2) / (2.0 * horiz), pts.astype(np.int32)

    def _run_loop(self, camera_index):
        # Initialize Detector (supports MediaPipe 1.0+ Tasks or legacy Solutions)
        detector = None
        legacy_mode = False

        if hasattr(mp, "solutions") and hasattr(mp.solutions, "face_mesh"):
            mp_face_mesh = mp.solutions.face_mesh
            detector = mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            legacy_mode = True
        else:
            model_path = ensure_model_exists()
            if model_path:
                from mediapipe.tasks import python
                from mediapipe.tasks.python import vision
                base_options = python.BaseOptions(model_asset_path=model_path)
                options = vision.FaceLandmarkerOptions(
                    base_options=base_options,
                    output_face_blendshapes=False,
                    output_facial_transformation_matrixes=False,
                    num_faces=1
                )
                detector = vision.FaceLandmarker.create_from_options(options)

        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            self.running = False
            return

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.03)
                continue

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            landmarks = None
            if detector is not None:
                if legacy_mode:
                    results = detector.process(rgb)
                    if results.multi_face_landmarks:
                        landmarks = results.multi_face_landmarks[0].landmark
                else:
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                    results = detector.detect(mp_image)
                    if results.face_landmarks:
                        landmarks = results.face_landmarks[0]

            ear = 0.0
            if landmarks is not None:
                left_ear, left_pts = self._calc_ear(landmarks, self.LEFT_EYE, w, h)
                right_ear, right_pts = self._calc_ear(landmarks, self.RIGHT_EYE, w, h)
                ear = (left_ear + right_ear) / 2.0

                # Draw landmark contours on the RGB frame
                cv2.polylines(rgb, [left_pts], isClosed=True, color=(0, 255, 255), thickness=1)
                cv2.polylines(rgb, [right_pts], isClosed=True, color=(0, 255, 255), thickness=1)

                if ear < self.ear_threshold:
                    self.closed_frames += 1
                    if self.closed_frames >= self.frame_limit:
                        if not self.is_drowsy:
                            self.drowsy_event_count += 1
                        self.is_drowsy = True

                        if self.alarm_enabled:
                            now = time.time()
                            if now - self.last_alarm_time > 0.6:
                                self.last_alarm_time = now
                                threading.Thread(target=trigger_beep, daemon=True).start()

                        if self.on_drowsiness_callback:
                            self.on_drowsiness_callback(True)
                else:
                    self.closed_frames = max(0, self.closed_frames - 1)
                    self.is_drowsy = False
                    if self.on_drowsiness_callback:
                        self.on_drowsiness_callback(False)
            else:
                self.is_drowsy = False
                self.closed_frames = 0

            with self.lock:
                self.current_ear = ear
                self.latest_frame = Image.fromarray(rgb)

            time.sleep(0.015)

        if self.cap:
            self.cap.release()
        if detector and hasattr(detector, 'close'):
            detector.close()

    def get_snapshot(self):
        with self.lock:
            return {
                "ear": self.current_ear,
                "closed_frames": self.closed_frames,
                "is_drowsy": self.is_drowsy,
                "event_count": self.drowsy_event_count,
                "frame": self.latest_frame
            }
