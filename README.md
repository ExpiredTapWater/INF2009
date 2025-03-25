### Raspberry Pi Zero Setup
1. Install 64-bit Lite OS via Pi Imager
    - Using config, setup Wifi and enable SSH
2. Update and install git
    - `sudo apt update && sudp apt upgrade -y` (Update)
    - `sudo reboot` (reboot)
    - `sudo apt install git` (Install git)
3. Install drivers
    - The original repo seems to be depreciated, and did not work when I tested it.
    - Need to use 3rd party libraries:
        - `git clone -b v6.6 https://github.com/HinTak/seeed-voicecard.git`
            - Clone the correct branch! 
            - Check kernal version and use the corresponding branch! (Bookworm should be v6.6.xxx)
        - `cd seeed-voicecard` (Change directory)
        - `sudo ./install.sh` (Run install script)
        - `sudo reboot`
4. Test drivers:
    - `arecord -l` (Check ID, mine is 1)
    - `arecord -D "plughw:1,0" -f S16_LE -r 16000 -d 5 -t wav test.wav` (Record a short audio clip)
    - `aplay -D "plughw:1,0" test.wav` (Playback via 3.5mm)
