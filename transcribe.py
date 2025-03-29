import os
from pvcheetah import create
from pvrecorder import PvRecorder

cheetah = create(access_key=os.getenv("PICOVOICE_KEY"))

try:
    print('Cheetah version:', cheetah.version)

    recorder = PvRecorder(frame_length=cheetah.frame_length)
    recorder.start()
    print('Listening... (press Ctrl+C to stop)')

    while True:
        partial_transcript, is_endpoint = cheetah.process(recorder.read())
        print(partial_transcript, end='', flush=True)
        if is_endpoint:
            print(cheetah.flush())

except KeyboardInterrupt:
    print('\nStopped by user.')

finally:
    recorder.stop()
    cheetah.delete()
