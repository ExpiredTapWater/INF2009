# ----------------- Import Stuff ------------------
import os
import time
import threading
import RPi.GPIO as GPIO
import pvporcupine
from pvcheetah import create
from pvrecorder import PvRecorder
from Drivers.pixels import Pixels

# --------------- Setup Environment ---------------
key = os.getenv("PICOVOICE_KEY")
audio_device_index = -1  # Default device
override = threading.Event()
BUTTON_PIN = 17

# ----------------- Setup Button ------------------ 
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def on_button_press(channel):
    print("[DEBUG] Button pressed — forcing wake!")
    override.set()

GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=on_button_press, bouncetime=200)

# ---------------- Setup PicoVoice ----------------
def setup_porcupine():

    # Basic setup
    keywords = ["porcupine", "raspberry pi"]
    sensitivities = [0.8 , 0.8]  # Sensitivity per keyword
    
    # Prepare keywords
    keyword_paths = [
        pvporcupine.KEYWORD_PATHS["porcupine"],
        "./PicoVoice/wake_word.ppn"
    ]

    keywords_formatted = [k for k in keywords]

    # Initialize
    porcupine = pvporcupine.create(
        access_key=key,
        keyword_paths=keyword_paths,
        sensitivities=sensitivities
    )

    print("Porcupine Ready")

    # DEBUG: confirm if frame length is the sam for cheetah: YES (512)
    # print(f"DEBUG: Porcupine Frame: {porcupine.frame_length} ")

    return porcupine, keywords_formatted

def setup_cheetah():

    print("Initializing Cheetah")
    cheetah = create(access_key=key,
                     endpoint_duration_sec=0.5,
                     enable_automatic_punctuation=False)
    print("Cheetah Ready")
    
    return cheetah

def setup_recorder():

    # Initialize Mic Input
    recorder = PvRecorder(
        frame_length=512,
        device_index=audio_device_index
    )

    recorder.start()
    print("Input Device Ready")

    return recorder

def setup_LED():

    pixels = Pixels()
    pixels.wakeup()

    return pixels

# ---------- Main Function Start ----------
def main():

    # Setup LED
    pixels = setup_LED()

    # Get wake-word model instance
    porcupine, keywords_formatted = setup_porcupine()
    
    # Get speech to text model instance
    cheetah = setup_cheetah()

    # Setup audio input
    recorder = setup_recorder()

    # Turn pixels off once ready
    pixels.off()

    try:

        # Run forever
        while True:
            
            # Get audio frame
            pcm = recorder.read()

            # Check for wake word
            result = porcupine.process(pcm)

            # If wake word detected or button override is used
            if result >= 0 or override.is_set():

                # Reset flag 
                override.clear() 

                # Play LED animation
                pixels.think()

                # FOR DEBUG ONLY ----------------------------------------------
                if result >= 0:
                    print(f"[DEBUG] Detected: '{keywords_formatted[result]}'")
                else:
                    print("[DEBUG] Wake triggered by button")
                # FOR DEBUG ONLY ----------------------------------------------

                start_time = time.time()

                while True:
                    frame = recorder.read()
                    partial_transcript, is_endpoint = cheetah.process(frame)
                    print(partial_transcript, end='', flush=True)

                    if is_endpoint:
                        final_transcript = cheetah.flush()
                        print(f"\n[Final Transcript] {final_transcript}")
                        print("[OK] Transcription complete")
                        pixels.blink('green')
                        break

                    # Check for timeout
                    if time.time() - start_time > 10:
                        print("\n[ERR] Transcription timeout")
                        pixels.blink('red')
                        break

    except KeyboardInterrupt:
        print("Stopping...")

    finally:
        porcupine.delete()
        cheetah.delete()
        recorder.delete()

if __name__ == "__main__":
    main()