import cv2

def list_cameras():
    print("Searching for available cameras (Indices 0-5)...")
    available_cameras = []
    
    for i in range(6):
        try:
            # CAP_DSHOW is often faster on Windows for listing
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    print(f"[FOUND] Camera Index {i}: Resolution {int(width)}x{int(height)}")
                    available_cameras.append(i)
                cap.release()
            else:
                pass
                # print(f"[NOT FOUND] Camera Index {i}")
        except Exception as e:
            print(f"Error checking index {i}: {e}")

    print("\nSummary:")
    if not available_cameras:
        print("No cameras found! Ensure DroidCam is connected and 'Start' is clicked.")
    else:
        print(f"Available Indices: {available_cameras}")
        print("Likely Candidates:")
        print("  - Index 0: Usually built-in webcam")
        print("  - Index 1 or 2: Often DroidCam or external USB cameras")

if __name__ == "__main__":
    list_cameras()
