import cv2
import threading
import time
import queue
import os
import numpy as np
import torch
from ultralytics import YOLO
from engine.shared_state import state
import backend.core.config as config

class ThreadedStream:
    def __init__(self, source):
        # On Windows, using CAP_DSHOW can sometimes verify webcam access better for index 0
        if isinstance(source, int):
            self.cap = cv2.VideoCapture(source, cv2.CAP_DSHOW)
        else:
            self.cap = cv2.VideoCapture(source)
            
        if not self.cap.isOpened():
            raise Exception(f"Could not open video source {source}")
            
        self.q = queue.Queue(maxsize=1) # Minimal buffer for zero lag
        self.running = True
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                self.running = False
                break
            if not self.q.empty():
                try:
                    self.q.get_nowait() # Discard old frame
                except queue.Empty:
                    pass
            self.q.put(frame)

    def read(self):
        try:
            return True, self.q.get(timeout=1.0)
        except queue.Empty:
            return False, None

    def release(self):
        self.running = False
        if self.cap.isOpened():
            self.cap.release()

class VisionEngine(threading.Thread):
    def __init__(self, source=None):
        super().__init__()
        # Use env var if source not provided
        if source is None:
            env_source = os.getenv("CAMERA_SOURCE", "0")
            if env_source.isdigit():
                self.source = int(env_source)
            else:
                self.source = env_source
        else:
            self.source = source
            
        # Mission V6: Hardware Awareness
        self.cuda_available = torch.cuda.is_available()
        self.device_str = '0' if self.cuda_available else 'cpu'
        self.half_precision = self.cuda_available # FP16 on GPU
        self.inference_imgsz = 1080 if self.cuda_available else 480
        
        print(f"[VisionEngine] Mission V6 Hardware: {'GPU (RTX)' if self.cuda_available else 'CPU (HP)'}")
        print(f"[VisionEngine] Settings: Device={self.device_str}, imgsz={self.inference_imgsz}, half={self.half_precision}")

        self.running = False
        self.model = None
        self.homography_matrix = None 
        self.last_fps_time = time.time()
        self.frame_count = 0
        self.stream = None

    def set_homography(self, matrix_list):
        try:
            self.homography_matrix = np.array(matrix_list, dtype=np.float32)
            print("[VisionEngine] Homography Matrix Updated")
        except Exception as e:
            print(f"[VisionEngine] Error setting homography: {e}")

    def run(self):
        """Unified Inference Loop V6"""
        print(f"[VisionEngine] Loading Model: {config.YOLO_MODEL}")
        try:
            self.model = YOLO(config.YOLO_MODEL)
            self.model.to(self.device_str)
        except Exception as e:
            print(f"[VisionEngine] Fatal Error loading model: {e}")
            return

        print(f"[VisionEngine] Starting ThreadedStream on {self.source}")
        try:
            self.stream = ThreadedStream(self.source)
        except Exception as e:
            print(f"[VisionEngine] Stream Error: {e}")
            return

        self.running = True
        
        while self.running:
            ret, frame = self.stream.read()
            if not ret:
                print("[VisionEngine] Capture stopped or disconnected.")
                break

            # Metrics Tracking (V6 System Pulse)
            self.frame_count += 1
            now = time.time()
            if now - self.last_fps_time >= 1.0:
                fps = self.frame_count / (now - self.last_fps_time)
                vram = 0
                if self.cuda_available:
                    vram = torch.cuda.memory_reserved(0) / 1024**2 # MB
                
                state.update_metrics(round(fps, 1), round(vram, 1), "GPU" if self.cuda_available else "CPU")
                self.frame_count = 0
                self.last_fps_time = now

            try:
                # Inference with Mission V6 Adaptive Params
                results = self.model.predict(
                    source=frame,
                    device=self.device_str,
                    half=self.half_precision,
                    imgsz=self.inference_imgsz,
                    conf=config.CONF_THRESHOLD,
                    iou=config.IOU_THRESHOLD,
                    verbose=False,
                    classes=[0] # Only persons
                )
                
                person_count = 0
                for r in results:
                    person_count = len(r.boxes)
                
                annotated_frame = results[0].plot()

                # Coordinate Mapping V8: Foot-to-Floor Accuracy
                coordinates = []
                for r in results:
                    for box in r.boxes:
                        # xyxy gives us [x1, y1, x2, y2]
                        x1, y1, x2, y2 = box.xyxy[0].tolist() 
                        
                        # Calculate Bottom-Center (Ground Contact Point)
                        foot_x = (x1 + x2) / 2
                        foot_y = y2
                        
                        # Normalize relative to source frame
                        norm_x = foot_x / frame.shape[1]
                        norm_y = foot_y / frame.shape[0]
                        
                        coord_entry = {
                            "x": norm_x, "y": norm_y,
                            "pixel_x": foot_x, "pixel_y": foot_y
                        }

                        if self.homography_matrix is not None:
                            # Apply Homography to Foot-to-Floor point
                            pt = np.array([[[norm_x, norm_y]]], dtype=np.float32)
                            try:
                                dst = cv2.perspectiveTransform(pt, self.homography_matrix)
                                map_x = float(dst[0][0][0])
                                map_y = float(dst[0][0][1])
                                
                                # Safety: Check if actually on floor plan (0.0 - 1.0)
                                if 0 <= map_x <= 1 and 0 <= map_y <= 1:
                                    coord_entry["map_x"] = map_x
                                    coord_entry["map_y"] = map_y
                                else:
                                    # Still log it but maybe flag as out-of-bounds visually
                                    coord_entry["map_x"] = map_x
                                    coord_entry["map_y"] = map_y
                                    coord_entry["out_of_bounds"] = True
                            except Exception as e:
                                print(f"[VisionEngine] Mapping Warning: {e}")
                                pass

                        coordinates.append(coord_entry)

                # Determine Risk Level
                if person_count >= config.CROWD_DENSITY_HIGH:
                    risk = "DANGER"
                elif person_count >= config.CROWD_DENSITY_MEDIUM:
                    risk = "HIGH"
                else:
                    risk = "NORMAL"

                # Encode to JPEG
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
                ret, buffer = cv2.imencode('.jpg', annotated_frame, encode_param)
                if ret:
                    state.update_vision(buffer.tobytes(), person_count, risk, coordinates)
            
            except Exception as e:
                print(f"[VisionEngine] Inference Error: {e}")
                continue

    def stop(self):
        self.running = False
        if self.stream:
            self.stream.release()
