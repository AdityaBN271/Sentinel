import pyaudio

p = pyaudio.PyAudio()
print("Available Audio Devices:")
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    try:
        # Filter for input devices
        if info['maxInputChannels'] > 0:
            print(f"Index {i}: {info['name']} (Channels: {info['maxInputChannels']}, Rate: {info['defaultSampleRate']})")
    except Exception as e:
        print(f"Error reading device {i}: {e}")

p.terminate()
