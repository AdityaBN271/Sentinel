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
        self.homography_matrix = None # Numpy array for coord transformation

    def set_homography(self, matrix_list):
        try:
            self.homography_matrix = np.array(matrix_list, dtype=np.float32)
            print("[VisionEngine] Homography Matrix Updated")
        except Exception as e:
            print(f"[VisionEngine] Error setting homography: {e}")

    def capture_loop(self):
        """Producer: Reads frames as fast as possible."""
        while self.running:
            print(f"[VisionEngine] Attempting to open Source: {self.source}")
            
            # On Windows, using CAP_DSHOW can sometimes verify webcam access better for index 0
            if isinstance(self.source, int):
                cap = cv2.VideoCapture(self.source, cv2.CAP_DSHOW)
            else:
                cap = cv2.VideoCapture(self.source)
            
            if not cap.isOpened():
                print(f"[VisionEngine] ERROR: Could not open source {self.source}. Retrying in 5s...")
                time.sleep(5)
                continue
            
            print(f"[VisionEngine] Source {self.source} opened successfully.")
            
            while self.running and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("[VisionEngine] WARN: Failed to read frame (stream ended or disconnected). Reconnecting...")
                    break
                
                # Put frame in queue (drop old if full)
                if self.frame_queue.full():
                    try:
                        self.frame_queue.get_nowait()
                    except queue.Empty:
                        pass
                
                self.frame_queue.put(frame)
                
                # Sleep slightly to prevent CPU hogging if source is very fast (optional)
                # time.sleep(0.001)

            cap.release()
            print("[VisionEngine] Capture stopped or disconnected.")
            
            if self.running:
                print("[VisionEngine] Waiting 2s before retry...")
                time.sleep(2)

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
        
        import numpy as np # Ensure numpy is available in scope or global
        
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
                    
                    coord_enrty = {
                        "x": norm_x, 
                        "y": norm_y,
                        "pixel_x": x,
                        "pixel_y": y
                    }

                    # Apply Homography if available
                    if self.homography_matrix is not None:
                        # perspectiveTransform expects shape (1, N, 2)
                        pt = np.array([[[x, y]]], dtype=np.float32)
                        try:
                            dst = cv2.perspectiveTransform(pt, self.homography_matrix)
                            map_x = dst[0][0][0]
                            map_y = dst[0][0][1]
                            coord_enrty["map_x"] = float(map_x)
                            coord_enrty["map_y"] = float(map_y)
                        except Exception as e:
                            print(f"Transform Error: {e}")

                    coordinates.append(coord_enrty)

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
