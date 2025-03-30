# ----------------- Import Stuff ------------------
import os
import time
import threading
import pvporcupine
from pvcheetah import create
from pvrecorder import PvRecorder
from gpiozero import Button
from Drivers.pixels import Pixels

# --------------- Setup Environment ---------------
KEY = os.getenv("PICOVOICE_KEY")
AUDIO_DEVICE = -1  # Default device
FRAME_LENGTH = 512
TIMEOUT = 10 # In seconds

# ----------------- Button Setup ------------------
button = Button(17)
bypass_event = threading.Event()

def bypass_wake():
    bypass_event.set()

button.when_pressed = bypass_wake
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
        access_key=KEY,
        keyword_paths=keyword_paths,
        sensitivities=sensitivities
    )

    print("Porcupine Ready")

    # DEBUG: confirm if frame length is the sam for cheetah: YES (512)
    # print(f"DEBUG: Porcupine Frame: {porcupine.frame_length} ")

    return porcupine, keywords_formatted

def setup_cheetah():

    print("Initializing Cheetah")
    cheetah = create(access_key=KEY,
                     endpoint_duration_sec=0.5,
                     enable_automatic_punctuation=False)
    print("Cheetah Ready")
    
    return cheetah

def setup_recorder():

    # Initialize Mic Input
    recorder = PvRecorder(
        frame_length=FRAME_LENGTH,
        device_index=AUDIO_DEVICE
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

            # If wake word detected
            if result >= 0 or bypass_event.is_set():

                bypass_event.clear()    # Reset for future presses
                pixels.think()          # Display LED animation

                ## DEBUG ONLY
                if result >= 0:
                    print(f"[DEBUG] Detected: '{keywords_formatted[result]}'")
                ## DEBUG ONLY

                start_time = time.time()
                full_transcript = ""

                while True:
                    frame = recorder.read()
                    partial_transcript, is_endpoint = cheetah.process(frame)
                    full_transcript += partial_transcript
                    print(partial_transcript, end='', flush=True)

                    if is_endpoint:
                        final_transcript = full_transcript + cheetah.flush()
                        print(f"\n[Final Transcript] {final_transcript}")
                        print("[OK] Transcription complete")
                        pixels.blink('green')
                        break

                    # Check for timeout
                    if time.time() - start_time > TIMEOUT:
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