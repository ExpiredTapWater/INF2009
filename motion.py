# ----------------- Import Stuff ------------------
import cv2
import time
import pyttsx3
import sqlite3
import datetime
from picamera2 import Picamera2

# --------------- Setup Environment ---------------
HAAR = False    # True = Use Background Subtraction
                # False = Use Haar Cascade

# SYSTEM
DATABASE_NAME = "reminders.db"
first_frame = None

# Text-To-Speech
VOICE_RATE = 125

# CAMERA
DELAY = 0.5
THRESHOLD = 2000
CAPTURE_ON_MOTION = False

# ------- Update Environment via Config.txt --------
# Easily override variables by using nano config.txt

config = {}
with open("config.txt") as f:
    for line in f:
        if "=" in line:
            key, value = line.strip().split("=", 1)
            config[key.strip()] = value.strip()

# Override variable if present
if "HAAR" in config:
    HAAR = config["HAAR"].lower() == "true"

if "CAPTURE" in config:
    CAPTURE_ON_MOTION = config["CAPTURE"].lower() == "true"

if "HAAR_THRESHOLD" in config:
    THRESHOLD = int(config["HAAR_THRESHOLD"])

if "HAAR_THRESHOLD" in config:
    VOICE_RATE = int(config["VOICE_RATE"])


# ------------- Setup Text-To-Speech --------------
engine = pyttsx3.init()
engine.setProperty('rate', VOICE_RATE) # Speed
engine.setProperty('volume', 1.0)      # Max Volume

#--------------- Database Functions ---------------
def create_table():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            text TEXT,
            modified_text TEXT
        )
    """)
    conn.commit()
    conn.close()

# Retrieve the last inserted reminder:
def get_reminder():

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    try:
        # Get the last reminder
        cursor.execute("""
            SELECT * FROM reminders
            ORDER BY id DESC
            LIMIT 1
        """)
        row = cursor.fetchone()

        if row:
            reminder_id, name, text, modified_text = row

            # Delete the retrieved reminder
            cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
            conn.commit()
            print(f"Retrieved and deleted reminder with ID {reminder_id}")

            # Convert to your expected dictionary format
            reminder = {
                "Name": name,
                "Text": text,
                "Modified_Text": modified_text
            }
            return reminder
        else:
            print("No reminder found.")
            return None

    except Exception as e:
        print(f"Error retrieving and deleting last reminder: {e}")
        return None
    finally:
        conn.close()

# ----------------- Camera Setup ------------------
if HAAR:
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    print(f"Threshold: {THRESHOLD}")
else:
    print("Background frame capture in 2 seconds...")

# Initialize Pi Camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
picam2.start()

# Give camera time to warm up
time.sleep(2)

# ------------------ Main Loop --------------------

def HAAR_detection():
    print("Detection Using: HAAR Cascade")
    pass

def subtractive_detection():
    print(f"Detection Using: Background Subtraction")

    global first_frame

    while True:
        frame = picam2.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if first_frame is None:
            first_frame = gray
            print("Background Frame Initialized")
            continue

        frame_delta = cv2.absdiff(first_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)

        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        motion_detected = False
        for contour in contours:
            if cv2.contourArea(contour) < 2000:
                continue
            motion_detected = True
            break

        if motion_detected:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            print(f"Motion detected at {timestamp}")

            reminder = get_reminder()
            if reminder["Modified_Text"] != "":
                engine.say(reminder["Modified_Text"])
                engine.runAndWait()

            elif reminder["Text"] != "":
                engine.say(reminder["Text"])
                engine.runAndWait()

            else:
                print("No text found on reminder")

            if CAPTURE_ON_MOTION:
                cv2.imwrite(f"motion_{timestamp}.jpg", frame)

        time.sleep(DELAY)

#-------------- Main Function --------------
def main():

    try:
        create_table()
        if HAAR:
            HAAR_detection()
        else:
            subtractive_detection()

    except KeyboardInterrupt:
        print("Stopping, please wait...")

    finally:
        picam2.stop()

if __name__ == '__main__':
    main()

