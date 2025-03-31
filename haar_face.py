import cv2
from picamera2 import Picamera2
import time

# Load Haar cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Initialize PiCamera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
picam2.start()

print("🧠 Starting frontal face detection...")
time.sleep(2)  # Give camera time to warm up

while True:
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=4,
        minSize=(40, 40)
    )

    if len(faces) > 0:
        print(f"👤 Detected {len(faces)} face(s)")
        for (x, y, w, h) in faces:
            # Optional: Draw rectangle
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Optional: Save frame
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        cv2.imwrite(f"face_{timestamp}.jpg", frame)

    time.sleep(0.5)