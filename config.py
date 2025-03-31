import streamlit as st
import configparser

def load_config(filepath="config.txt"):
    """Loads configuration from the given file."""
    config = configparser.ConfigParser()
    config.read(filepath)
    if 'DEFAULT' not in config:
        config['DEFAULT'] = {}  # Ensure DEFAULT section exists
    return config

def save_config(config, filepath="config.txt"):
    """Saves configuration to the given file."""
    with open(filepath, 'w') as configfile:
        config.write(configfile)

def main():
    st.title("Config.txt Modifier")

    config = load_config()

    # Create UI elements to modify the config values
    local_only = st.checkbox("LOCAL_ONLY", config.getboolean("DEFAULT", "LOCAL_ONLY"))
    local_tts = st.checkbox("LOCAL_TTS", config.getboolean("DEFAULT", "LOCAL_TTS"))
    apply_2nd_person = st.checkbox("APPLY_2ND_PERSON", config.getboolean("DEFAULT", "APPLY_2ND_PERSON"))
    voice_rate = st.number_input("VOICE_RATE", value=config.getint("DEFAULT", "VOICE_RATE"))
    haar = st.checkbox("HAAR", config.getboolean("DEFAULT", "HAAR"))
    haar_threshold = st.number_input("HAAR_THRESHOLD", value=config.getint("DEFAULT", "HAAR_THRESHOLD"))
    capture = st.checkbox("CAPTURE", config.getboolean("DEFAULT", "CAPTURE"))

    if st.button("Save Changes"):
        # Update config with new values
        config.set("DEFAULT", "LOCAL_ONLY", str(local_only))
        config.set("DEFAULT", "LOCAL_TTS", str(local_tts))
        config.set("DEFAULT", "APPLY_2ND_PERSON", str(apply_2nd_person))
        config.set("DEFAULT", "VOICE_RATE", str(voice_rate))
        config.set("DEFAULT", "HAAR", str(haar))
        config.set("DEFAULT", "HAAR_THRESHOLD", str(haar_threshold))
        config.set("DEFAULT", "CAPTURE", str(capture))

        save_config(config)
        st.success("Configuration saved!")

if __name__ == "__main__":
    main()