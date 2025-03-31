### Raspberry Pi Zero Setup (Recorder Unit)
1. Install 64-bit Lite OS via Pi Imager
    - Using config, setup Wifi and enable SSH
2. Update and install git

   ```
    sudo apt update && sudp apt upgrade -y
    sudo raspi-config # Enable SPI
    sudo reboot
    sudo apt install git
   ```

4. Install drivers
    - The original repo seems to be depreciated, and did not work when I tested it.
    - Need to use 3rd party libraries:
        - `git clone -b v6.6 https://github.com/HinTak/seeed-voicecard.git`
            - Clone the correct branch! 
            - Check kernal version and use the corresponding branch! (Bookworm should be v6.6.xxx)
        - `cd seeed-voicecard` (Change directory)
        - `sudo ./install.sh` (Run install script)
        - `sudo reboot`
    - Installing `spidev` and GPIO library:
        - `sudo apt install python3-dev portaudio19-dev` <-- Important!
        - `pip install spidev`
    - Fix: RuntimeError: Failed to add edge detection (Required for buttons)
        - `pip uninstall RPi.GPIO`
        - `pip install rpi-lgpio`
5. Test drivers:
    - `arecord -l` (Check ID, mine is 1)
    - `arecord -D "plughw:1,0" -f S16_LE -r 16000 -d 5 -t wav test.wav` (Record a short audio clip)
    - `aplay -D "plughw:1,0" test.wav` (Playback via 3.5mm)
6. Setup MQTT
    - Install Mosquitto and Mosquitto Clients:
        - `sudo apt install mosquitto mosquitto-clients -y`
    - Enable Mosquitto to start on boot:
        - `sudo systemctl enable mosquitto`
    - (Optional) Verify it is running:
        - `systemctl status mosquitto`

### PicoVoice Setup
1. Setup virtual environment
    - `mkdir venv` (Creates a folder to store all our environments)
    - `cd venv`
    - `python3 -m venv inf2009` (Creates an environement called "inf2009")
2. Update shell config file:
    - `sudo nano ~/.bashrc`
    - `export PICOVOICE_KEY="enter_api_key_here"`
    - (Optional) Add alias for easier development
        - Add `alias inf2009='source ~/venv/inf2009/bin/activate'`
        - You can now type `inf2009` to activate the environment
3. Install PicoVoice libraries (Or use requirements.txt)
    - `pip install pvporcupine` (Wake word detection)
    - `pip install pvcheeta` (Speech to Text)
4. Install Other libraries
    - `pip install paho-mqtt`

### Raspberry Pi 4 Setup (Main Unit)
1. Install 64-bit Lite OS via Pi Imager
    - Using config, setup Wifi and enable SSH
2. Update and install git, enable I2C 

   ```
    sudo apt update && sudp apt upgrade -y
    sudo raspi-config
    sudo reboot
    sudo apt install git
   ```
### spaCy, MQTT Setup
1. Setup virtual environment
    - `mkdir venv` (Creates a folder to store all our environments)
    - `cd venv`
    - `python3 -m venv inf2009` (Creates an environement called "inf2009")
2. (Optional) Add alias for easier development
    - `sudo nano ~/.bashrc`
    - Add `alias inf2009='source ~/venv/inf2009/bin/activate'`
    - You can now type `inf2009` to activate the environment
3. Install libraries:

    ```
    pip install spacy --prefer-binary
    python -m spacy download en_core_web_sm
    ```
4. Setup MQTT
    - Install Mosquitto and Mosquitto Clients:
        - `sudo apt install mosquitto mosquitto-clients -y`
    - Enable Mosquitto to start on boot:
        - `sudo systemctl enable mosquitto`
    - (Optional) Verify it is running:
        - `systemctl status mosquitto`
5. Camera Setup
    - `sudo apt install -y python3-picamera2`
    - `pip install opencv-python-headless`
    - `pip install imutils`

### Github Authentication Setup (During development only)
We'll need to create SSH keys in order to clone our private repo
1. Generate an SSH key on your Pi:
    - `ssh-keygen -t ed25519 -C "your-email@example.com"`
2. Copy the key and paste into github:
    - `cat ~/.ssh/id_ed25519.pub` (Prints key)
    - GitHub → Profile icon → Settings → SSH and GPG Keys → New SSH Key
3. Test connection:
    - `ssh -T git@github.com`

### Helpful Commands
- MQTT Debug
    - Listener: `mosquitto_sub -h localhost -t test/topic -v`
    - Publisher: `mosquitto_pub -h <IP_ADDR> -t test/topic -m "Hello from Pi"`
- PicoLLM Model Testing
    - After downloading, easily trasnfer to Pi via SCP:
    - Eg. `scp C:\Users\ChenYi\Documents\<FILE_NAME> chenyi@<IP_ADDR>:~/INF2009/`
