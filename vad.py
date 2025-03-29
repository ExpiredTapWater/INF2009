import os
import pvcobra
from pvrecorder import PvRecorder

def main():
    access_key = os.getenv("PICOVOICE_KEY")

    # Initialize Cobra
    cobra = pvcobra.create(access_key=access_key)

    # Set up audio recording
    recorder = PvRecorder(frame_length=512, device_index=-1)  # -1 = default mic
    recorder.start()

    print("Listening for voice activity... (Ctrl+C to stop)")

    try:
        while True:
            pcm = recorder.read()  # Get raw PCM audio from mic
            voice_probability = cobra.process(pcm)  # Get voice level (0.0 to 1.0)
            print("Voice probability:", voice_probability)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        recorder.delete()
        cobra.delete()


if __name__ == "__main__":
    main()
