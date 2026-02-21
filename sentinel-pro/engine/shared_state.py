import threading
import time

class SharedState:
    def __init__(self):
        self._lock = threading.Lock()
        self.latest_frame = None  # JPEG bytes
        self.people_count = 0
        self.risk_level = "SAFE"
        self.audio_status = "NORMAL"
        self.last_update = time.time()
        self.zones = {} # Example: {"zone1": 5, "zone2": 10}
        self.coordinates = [] # List of {"x": float, "y": float}
        self.fps = 0.0
        self.vram_usage = 0.0 # in MB
        self.inference_device = "CPU"

    def update_vision(self, frame_jpeg, count, risk, coordinates=[]):
        with self._lock:
            self.latest_frame = frame_jpeg
            self.people_count = count
            self.risk_level = risk
            self.coordinates = coordinates
            self.last_update = time.time()

    def update_audio(self, status):
        with self._lock:
            self.audio_status = status
            self.last_update = time.time() # Or separate timestamp

    def update_metrics(self, fps, vram, device):
        with self._lock:
            self.fps = fps
            self.vram_usage = vram
            self.inference_device = device

    def get_snapshot(self):
        with self._lock:
            return {
                "people_count": self.people_count,
                "risk_level": self.risk_level,
                "audio_status": self.audio_status,
                "coordinates": self.coordinates,
                "fps": self.fps,
                "vram_usage": self.vram_usage,
                "inference_device": self.inference_device,
                "last_update": self.last_update
            }

    def get_frame(self):
        with self._lock:
            return self.latest_frame

# Global Singleton
state = SharedState()
