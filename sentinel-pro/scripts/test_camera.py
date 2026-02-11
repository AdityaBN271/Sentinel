import cv2
import time
import os

# Manual override - replace with your URL if .env reading fails
# URL = "http://192.168.x.x:8080/video" 

def test_camera():
    # Try to read from .env if possible, otherwise rely on hardcoded test
    try:
        with open("../backend/.env", "r") as f:
            for line in f:
                if line.startswith("CAMERA_SOURCE="):
                    source = line.strip().split("=", 1)[1]
                    break
    except:
        source = "0"
        print("Could not read .env, defaulting to 0")

    print(f"Testing Source: '{source}'")
    
    # If source looks like an int, convert it
    if source.isdigit():
        source = int(source)
    
    cap = cv2.VideoCapture(source)
    
    if not cap.isOpened():
        print("❌ FAILED: Could not open video source.")
        print("Suggestions:")
        print("1. Check if the IP address is correct.")
        print("2. Make sure phone and PC are on the SAME Wi-Fi.")
        print("3. Try opening the URL in Chrome/Edge. If it doesn't work there, it won't work here.")
        return

    print("✅ SUCCESS: Source opened! Reading frames...")
    
    start = time.time()
    frames = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ FAILED: Stream opened but could not read frame.")
            break
        
        frames += 1
        if frames % 30 == 0:
            print(f"Reading... {frames} frames captured.")
        
        cv2.imshow("Camera Test (Press 'q' to quit)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
        if frames > 100:
             print("Test successful. Closing...")
             break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_camera()
