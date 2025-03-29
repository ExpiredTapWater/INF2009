# ----------------- Import Stuff ------------------
import os
import pvporcupine
from pvcheetah import create
from pvrecorder import PvRecorder

# --------------- Setup Environment ---------------
key = os.getenv("PICOVOICE_KEY")

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
        access_key=key,
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
    print(f"DEBUG: Porcupine Frame: {porcupine.frame_length} ")
    return porcupine, recorder, keywords_formatted

# ---------- Real Time S2T Setup (Cheetah) ----------
def setup_cheetah():

    cheetah = create(access_key=key)
    print(f"DEBUG: Cheetah Frame: {cheetah.frame_length} ")


# ---------- Main Function Start ----------
def main():

    # Get porcupine instance
    porcupine, recorder, keywords_formatted = setup_porcupine()
    setup_cheetah()

    try:
        while True:
            pcm = recorder.read()
            result = porcupine.process(pcm)

            if result >= 0:
                print(f"Detected '{keywords_formatted[result]}'")

    except KeyboardInterrupt:
        print("Stopping...")

    finally:
        recorder.delete()
        porcupine.delete()

if __name__ == "__main__":
    main()