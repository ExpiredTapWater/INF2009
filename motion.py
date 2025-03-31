from picamera2 import Picamera2
import cv2
import time
import datetime
import numpy as np

# Initialize Pi Camera
picam2 = Picamera2()
picam2.configure(picam2.preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
picam2.start()

time.sleep(2)  # Give camera time to warm up

first_frame = None

print("🔍 Starting motion detection...")

while True:
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if first_frame is None:
        first_frame = gray
        print("📷 Initialized background frame.")
        continue

    frame_delta = cv2.absdiff(first_frame, gray)
    thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)

    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    motion_detected = False
    for contour in contours:
        if cv2.contourArea(contour) < 500:
            continue
        motion_detected = True
        break

    if motion_detected:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        print(f"🚨 Motion detected at {timestamp}")
        # Optional: save the frame as an image
        # cv2.imwrite(f"motion_{timestamp}.jpg", frame)

    time.sleep(1)  # adjust to control CPU usage and sensitivity
