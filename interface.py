import streamlit as st
import sqlite3
import os

DATABASE_NAME = "reminders.db"
CONFIG_PATH = "config.txt"

# --- Reminder DB Functions ---

def create_table():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            text TEXT,
            modified_text TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_reminder(reminder):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO reminders (name, text, modified_text)
            VALUES (?, ?, ?)
        """, (reminder["Name"], reminder["Text"], reminder["Modified_Text"]))
        conn.commit()
        st.success("Reminder inserted!")
    except Exception as e:
        st.error(f"Failed to insert reminder: {e}")
    finally:
        conn.close()

def get_all_reminders():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reminders")
    data = cursor.fetchall()
    conn.close()
    return data

def delete_reminder(reminder_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
    conn.commit()
    conn.close()

# --- Config Handling ---

def read_config(filepath):
    config = {}
    with open(filepath, "r") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                config[key.strip()] = value.strip()
    return config

def write_config(filepath, config_dict):
    with open(filepath, "w") as f:
        for key, value in config_dict.items():
            f.write(f"{key} = {value}\n")

# --- Streamlit UI ---

st.set_page_config(page_title="Reminder Manager", layout="wide")
st.title("Reminder Manager")

create_table()

# --- Reminder Input ---
st.subheader("Add a New Reminder")
with st.form("reminder_form"):
    cols = st.columns(3)
    name = cols[0].text_input("Name")
    text = cols[1].text_input("Text")
    modified_text = cols[2].text_input("Modified Text")
    submitted = st.form_submit_button("Add Reminder")
    if submitted:
        new_reminder = {"Name": name, "Text": text, "Modified_Text": modified_text}
        insert_reminder(new_reminder)
        st.rerun()

# --- Display Reminders ---
st.subheader("Current Reminders")
reminders = get_all_reminders()
if reminders:
    for reminder in reminders:
        id_, name, text, modified_text = reminder
        cols = st.columns([4, 4, 4, 1])
        with cols[0]:
            st.markdown(f"**Name:** {name}", unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f"**Text:** {text}", unsafe_allow_html=True)
        with cols[2]:
            st.markdown(f"**Modified:** {modified_text}", unsafe_allow_html=True)
        with cols[3]:
            if st.button("Delete", key=f"delete_{id_}"):
                delete_reminder(id_)
                st.rerun()
else:
    st.info("No reminders found.")

# --- Config Editor ---
st.subheader("Configuration Settings")
if os.path.exists(CONFIG_PATH):
    config = read_config(CONFIG_PATH)
    
    with st.form("config_form"):
        bool_keys = ["LOCAL_ONLY", "LOCAL_TTS", "APPLY_2ND_PERSON", "HAAR", "CAPTURE"]
        num_keys = ["VOICE_RATE", "THRESHOLD"]
        display_names = {"LOCAL_ONLY": "Local Only Mode", 
                    "LOCAL_TTS" : "Use offline Text-To-Speech", 
                    "APPLY_2ND_PERSON" : "Process Using LLM", 
                    "HAAR" : "Use HAAR Cascade for Motion Detection", 
                    "CAPTURE" : "Save Frames with Detected Motion",
                    "VOICE_RATE" : "Talking Speed For Local TTS",
                    "THRESHOLD" : "Threshold amount to be counted as motion (Default 2000)"}

        new_config = {}

        for key in bool_keys:
            current_value = config.get(key, "false").lower() == "true"
            display = display_names.get(key, "false")
            new_config[key] = st.checkbox(display, value=current_value)

        for key in num_keys:
            current_value = int(config.get(key, "0"))
            new_config[key] = st.number_input(key, value=current_value)

        if st.form_submit_button("Save Config"):
            # Convert booleans to "true"/"false"
            final_config = {k: ("true" if v else "false") if k in bool_keys else str(v) for k, v in new_config.items()}
            write_config(CONFIG_PATH, final_config)
            st.success("Configuration saved.")
else:
    st.error(f"Config file not found at {CONFIG_PATH}")
