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

    def get_snapshot(self):
        with self._lock:
            return {
                "people_count": self.people_count,
                "risk_level": self.risk_level,
                "audio_status": self.audio_status,
                "coordinates": self.coordinates,
                "last_update": self.last_update
            }

    def get_frame(self):
        with self._lock:
            return self.latest_frame

# Global Singleton
state = SharedState()
