import cv2
from picamera2 import Picamera2
import time

# Load pre-trained people detector (Haar cascade for full body)
people_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_upperbody.xml')

# Initialize camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
picam2.start()

print("🧍 Starting person detection...")
time.sleep(2)

while True:
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    # Detect people
    people = people_cascade.detectMultiScale(
        gray,
        scaleFactor=1.05,   # smaller steps = more detections, slower
        minNeighbors=1,     # lower = more sensitive
        minSize=(30, 30)    # detect smaller people
    )

    if len(people) > 0:
        print(f"🚨 Detected {len(people)} person(s)")
        for (x, y, w, h) in people:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Optional: save frame
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        cv2.imwrite(f"person_{timestamp}.jpg", frame)

    time.sleep(0.5)
