import threading
import time
import numpy as np
import pyaudio
import librosa
import joblib
import os
import queue
from backend.core.config import (
    AUDIO_RATE, AUDIO_CHUNK, AUDIO_BUFFER_SECONDS, 
    RMS_THRESHOLD, SPECTRAL_CENTROID_THRESHOLD, 
    PANIC_PERSISTENCE, AUDIO_MODEL_PATH
)
from engine.shared_state import state

class AudioEngine(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = False
        self.panic_counter = 0
        self.ml_model = None
        self.scaler = None
        self.ptr_lock = threading.Lock()
        
        # Load ML Model if exists
        if os.path.exists(AUDIO_MODEL_PATH):
            try:
                self.ml_model = joblib.load(AUDIO_MODEL_PATH) 
                print("[AudioEngine] ML Model loaded.")
            except:
                print("[AudioEngine] ML Model load failed, falling back to heuristics.")

    def detect_heuristic(self, y, sr):
        # RMS
        rms = librosa.feature.rms(y=y)
        rms_mean = np.mean(rms)
        
        # Centroid (Fast)
        cent = librosa.feature.spectral_centroid(y=y, sr=sr)
        cent_mean = np.mean(cent)
        
        # Logic
        is_panic = (rms_mean > RMS_THRESHOLD) and (cent_mean > SPECTRAL_CENTROID_THRESHOLD)
        return is_panic

    def run(self):
        print("[AudioEngine] Starting Audio Stream...")
        p = pyaudio.PyAudio()
        stream = None
        used_rate = AUDIO_RATE
        
        # Candidate rates to try if default fails
        rates_to_try = [AUDIO_RATE, 44100, 16000, 8000]
        # Remove duplicates while preserving order
        rates_to_try = list(dict.fromkeys(rates_to_try))

        # 1. Try Default Device with configured rate
        try:
            stream = p.open(format=pyaudio.paFloat32,
                            channels=1,
                            rate=AUDIO_RATE,
                            input=True,
                            frames_per_buffer=AUDIO_CHUNK)
            print(f"[AudioEngine] Connected to default input device at {AUDIO_RATE}Hz.")
        except Exception as e:
            print(f"[AudioEngine] Default device failed: {e}. Scanning devices...")

        # 2. Search for any working device/rate combination
        if stream is None:
            for i in range(p.get_device_count()):
                try:
                    info = p.get_device_info_by_index(i)
                    if info['maxInputChannels'] > 0:
                        # Try rates
                        for r in rates_to_try:
                            try:
                                stream = p.open(format=pyaudio.paFloat32,
                                                channels=1,
                                                rate=r,
                                                input=True,
                                                input_device_index=i,
                                                frames_per_buffer=AUDIO_CHUNK)
                                print(f"[AudioEngine] Connected to device {i} ({info['name']}) at {r}Hz")
                                used_rate = r
                                break
                            except:
                                continue
                        if stream: break
                except:
                    continue

        if stream is None:
             print("[AudioEngine] No working audio input device found. Audio analysis disabled.")
             print("[AudioEngine] HINT: Check Windows Microphone Privacy Settings and allow apps to access the microphone.")
             p.terminate()
             return

        self.running = True
        
        # Use used_rate for buffer calculation
        buffer_len = int(used_rate * AUDIO_BUFFER_SECONDS)
        audio_buffer = np.zeros(buffer_len, dtype=np.float32)

        while self.running:
            try:
                if stream.get_read_available() < AUDIO_CHUNK:
                    time.sleep(0.01)
                    continue

                data = stream.read(AUDIO_CHUNK, exception_on_overflow=False)
                chunk = np.frombuffer(data, dtype=np.float32)
                
                # Roll Buffer
                audio_buffer = np.roll(audio_buffer, -AUDIO_CHUNK)
                audio_buffer[-AUDIO_CHUNK:] = chunk
                
                # Detection using actual rate
                is_panic = self.detect_heuristic(audio_buffer, used_rate)
                
                # Temporal Smoothing
                if is_panic:
                    self.panic_counter += 1
                else:
                    self.panic_counter = max(0, self.panic_counter - 1)
                
                final_status = "PANIC" if self.panic_counter >= PANIC_PERSISTENCE else "NORMAL"
                
                # Update Hub
                state.update_audio(final_status)
                
            except Exception as e:
                 # print(f"[AudioEngine] {e}")
                 pass
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("[AudioEngine] Stopped.")

    def stop(self):
        self.running = False
