import sys
import os
import time

# Add project root to sys path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.audio.audio_module import AudioEngine

def test_audio_engine_startup():
    print("Initializing AudioEngine...")
    engine = AudioEngine()
    print("Starting AudioEngine thread...")
    engine.start()
    
    time.sleep(3) # Let it try to connect
    
    if engine.is_alive():
        print("AudioEngine thread is RUNNING.")
        if engine.running:
             print("AudioEngine internal state is RUNNING.")
        else:
             print("AudioEngine thread is alive but internal state is NOT running (might be shutting down).")
    else:
        print("AudioEngine thread is STOPPED.")

    print("Stopping AudioEngine...")
    engine.stop()
    engine.join()
    print("Test Complete.")

if __name__ == "__main__":
    test_audio_engine_startup()
