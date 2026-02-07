import serial
import time
import threading
from .config import ARDUINO_PORT, ARDUINO_BAUD

class ArduinoBridge:
    def __init__(self, port=ARDUINO_PORT, baud=ARDUINO_BAUD):
        self.port = port
        self.baud = baud
        self.serial_conn = None
        self.connected = False
        self.lock = threading.Lock()
        
        self.connect()

    def connect(self):
        try:
            self.serial_conn = serial.Serial(self.port, self.baud, timeout=1, write_timeout=0.1)
            time.sleep(2) # Wait for Arduino reboot
            self.connected = True
            print(f"[Serial] Connected to Arduino at {self.port}")
        except Exception as e:
            print(f"[Serial] Failed to connect to {self.port}: {e}")
            self.connected = False

    def send_command(self, command: str):
        if not self.connected:
            return
        
        with self.lock:
            try:
                # Command format: "RISK:HIGH\n"
                msg = f"{command}\n"
                self.serial_conn.write(msg.encode('utf-8'))
            except Exception as e:
                print(f"[Serial] Send Error: {e}")
                self.connected = False

    def close(self):
        if self.serial_conn:
            self.serial_conn.close()
