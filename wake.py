import os
import struct
import wave
from datetime import datetime

import pvporcupine
from pvrecorder import PvRecorder

def main():
    # === Configuration ===
    access_key = os.getenv("PICOVOICE_KEY")  # Replace with your actual AccessKey from Picovoice
    keywords = ["porcupine"]  # Default keyword(s) to detect
    sensitivities = [0.5]  # Sensitivity per keyword
    audio_device_index = -1  # Default device
    output_path = None  # Change to a path like "output.wav" if you want to save audio

    keyword_paths = [pvporcupine.KEYWORD_PATHS[k] for k in keywords]

    porcupine = pvporcupine.create(
        access_key=access_key,
        keyword_paths=keyword_paths,
        sensitivities=sensitivities
    )

    keywords_formatted = [k for k in keywords]
    print("Porcupine version:", porcupine.version)

    recorder = PvRecorder(
        frame_length=porcupine.frame_length,
        device_index=audio_device_index
    )
    recorder.start()

    wav_file = None
    if output_path is not None:
        wav_file = wave.open(output_path, "w")
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)

    print("Listening... (press Ctrl+C to exit)")

    try:
        while True:
            pcm = recorder.read()
            result = porcupine.process(pcm)

            if wav_file is not None:
                wav_file.writeframes(struct.pack("h" * len(pcm), *pcm))

            if result >= 0:
                print(f"[{datetime.now()}] Detected '{keywords_formatted[result]}'")

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        recorder.delete()
        porcupine.delete()
        if wav_file is not None:
            wav_file.close()


if __name__ == "__main__":
    main()
