# ---------- Import Stuff ----------
import os
import struct
import wave
from datetime import datetime

# ---------- PicoVoice ----------
import pvporcupine
from pvrecorder import PvRecorder

# ---------- Setup Environment ----------
access_key = os.getenv("PICOVOICE_KEY")

# ---------- Wake Word (Porcupine) Setup ----------
def setup_porcupine():

    # Basic setup
    keywords = ["porcupine", "raspberry pi"]
    sensitivities = [0.5 , 0.5]  # Sensitivity per keyword
    audio_device_index = -1  # Default device

    # Prepare keywords
    keyword_paths = [
        pvporcupine.KEYWORD_PATHS["porcupine"],
        "./PicoVoice/wake_word.ppn"
    ]

    keywords_formatted = [k for k in keywords]

    # Initialize
    porcupine = pvporcupine.create(
        access_key=access_key,
        keyword_paths=keyword_paths,
        sensitivities=sensitivities
    )

    # Initialize Mic Input
    recorder = PvRecorder(
        frame_length=porcupine.frame_length,
        device_index=audio_device_index
    )

    recorder.start()

    print("Porcupine Ready")
    return porcupine, recorder, keywords_formatted

def main():

    # Get porcupine instance
    porcupine, recorder, keywords_formatted = setup_porcupine()

    try:
        while True:
            pcm = recorder.read()
            result = porcupine.process(pcm)

            if result >= 0:
                print(f"[{datetime.now()}] Detected '{keywords_formatted[result]}'")

    except KeyboardInterrupt:
        print("Stopping...")

    finally:
        recorder.delete()
        porcupine.delete()