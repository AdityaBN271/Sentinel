import cv2
import threading
import time
import queue
import os
from ultralytics import YOLO
from engine.shared_state import state
from backend.core.config import YOLO_MODEL, CROWD_DENSITY_HIGH, CROWD_DENSITY_MEDIUM, IMG_SIZE

class VisionEngine(threading.Thread):
    def __init__(self, source=None):
        super().__init__()
        # Use env var if source not provided, parse as int if digit (webcam), else string (RTSP)
        if source is None:
            env_source = os.getenv("CAMERA_SOURCE", "0")
            if env_source.isdigit():
                self.source = int(env_source)
            else:
                self.source = env_source
        else:
            self.source = source
            
        self.running = False
        self.model = None
        self.frame_queue = queue.Queue(maxsize=1) # Keep only latest frame
        self.capture_thread = None

    def capture_loop(self):
        """Producer: Reads frames as fast as possible."""
        print(f"[VisionEngine] Opening Source: {self.source}")
        cap = cv2.VideoCapture(self.source)
        
        while self.running and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Put frame in queue (drop old if full)
            if self.frame_queue.full():
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    pass
            
            self.frame_queue.put(frame)
            
            # Limit capture rate slightly if needed, but usually we run max
            # time.sleep(0.001)

        cap.release()
        print("[VisionEngine] Capture stopped.")

    def run(self):
        """Consumer: Inference Loop"""
        print(f"[VisionEngine] Loading Model (TensorRT preferred): {YOLO_MODEL}")
        
        # Check for TensorRT engine
        model_path = YOLO_MODEL
        if YOLO_MODEL.endswith('.pt'):
            engine_path = YOLO_MODEL.replace('.pt', '.engine')
            # Logic to check if engine exists would go here
            # model_path = engine_path if os.path.exists(engine_path) else YOLO_MODEL
        
        self.model = YOLO(model_path)
        self.running = True
        
        # Start Producer
        self.capture_thread = threading.Thread(target=self.capture_loop, daemon=True)
        self.capture_thread.start()
        
        frame_counter = 0
        
        while self.running:
            try:
                # Wait for frame (blocking)
                frame = self.frame_queue.get(timeout=1.0)
            except queue.Empty:
                continue

            frame_counter += 1
            
            # Frame Skipping (Every 2nd frame)
            if frame_counter % 2 != 0:
                continue

            # Inference
            results = self.model(frame, verbose=False, classes=[0], imgsz=IMG_SIZE, half=True)
            
            person_count = 0
            
            for r in results:
                person_count = len(r.boxes)
            
            # Draw Bounding Boxes on the frame
            annotated_frame = results[0].plot()

            # Coordinates for heatmap (centroids)
            coordinates = []
            for r in results:
                for box in r.boxes:
                    # box.xywh returns center_x, center_y, width, height
                    x, y, w, h = box.xywh[0].tolist() 
                    # Normalize coordinates (0-1) for heatmap grid
                    norm_x = x / frame.shape[1]
                    norm_y = y / frame.shape[0]
                    coordinates.append({"x": norm_x, "y": norm_y})

            # Determine Status
            if person_count >= CROWD_DENSITY_HIGH:
                status = "HIGH"
            elif person_count >= CROWD_DENSITY_MEDIUM:
                status = "MEDIUM"
            else:
                status = "LOW"

            # Encode to JPEG for streaming
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            if ret:
                jpg_bytes = buffer.tobytes()
                # Update Shared State
                state.update_vision(jpg_bytes, person_count, status, coordinates)
            
            # Log FPS (Optional)
            # print(f"FPS: ...")

    def stop(self):
        self.running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=1)
