import cv2
import imutils

# Use Pi camera or USB camera (usually index 0)
cap = cv2.VideoCapture(0)
first_frame = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if first_frame is None:
        first_frame = gray
        continue

    frame_delta = cv2.absdiff(first_frame, gray)
    thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)

    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

    motion_detected = False
    for c in contours:
        if cv2.contourArea(c) < 500:
            continue
        motion_detected = True
        break

    if motion_detected:
        print(f"Motion detected!")

cap.release()
