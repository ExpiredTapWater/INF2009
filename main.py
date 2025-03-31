# ----------------- Import Stuff ------------------
import os
import re
import spacy
import sqlite3
import picollm
import paho.mqtt.client as mqtt
from google import genai

# --------------- Setup Environment ---------------
# MQTT
MQTT_BROKER = "localhost"
MQTT_TOPIC = "pi/transcript"
MQTT_PORT = 1883

# LLM
LLM_PATH = './phi3.5-289.pllm'
KEY = os.getenv("PICOVOICE_KEY")
GEMINI_KEY = os.getenv("GEMINI_KEY")
LLM = None

# NLP
NLP = None

# SYSTEM
LOCAL_ONLY = False
APPLY_2ND_PERSON = False
DATABASE_NAME = "reminders.db"

#----------- Database Functions ------------
def create_table():

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            name TEXT PRIMARY KEY,
            text TEXT,
            modified_text TEXT
        )
    """)
    conn.commit()
    conn.close()

# Inserts a reminder into the database.
def insert_reminder(reminder):

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO reminders (name, text, modified_text)
            VALUES (?, ?, ?)
        """, (reminder["Name"], reminder["Text"], reminder["Modified_Text"]))
        conn.commit()
        print("Inserted:", reminder)
    except sqlite3.IntegrityError:
        print(f"Entry for '{reminder['Name']}' already exists.")
    finally:
        conn.close()

# ------- Update Environment via Config.txt --------
# Easily override variables by using nano config.txt

config = {}
with open("config.txt") as f:
    for line in f:
        if "=" in line:
            key, value = line.strip().split("=", 1)
            config[key.strip()] = value.strip()

# Override variable if present
if "LOCAL_ONLY" in config:
    LOCAL_ONLY = config["LOCAL_ONLY"].lower() == "true"
    print(f"Local Only Mode: {LOCAL_ONLY}")

if "APPLY_2ND_PERSON" in config:
    APPLY_2ND_PERSON = config["APPLY_2ND_PERSON"].lower() == "true"
    print(f"Apply 2nd Person Transform: {APPLY_2ND_PERSON}")

# --------------- LLM Setup ---------------

LOCAL_PROMPT = ("Rewrite the sentence in second person. Respond in the following format: OUTPUT: <Text>\n{TEXT}")
GEMINI_PROMPT = "Rewrite the following instruction so that it directly addresses the person using second-person pronouns (you, your): {text} Only respond with the text"

# Loads the local or Cloud LLM model
def load_LLM(LOCAL_ONLY):

    global LLM

    # Use PicoLLM
    if LOCAL_ONLY:
        print(f"Loading LLM from: {LLM_PATH}")
        LLM = picollm.create(access_key=KEY,model_path=LLM_PATH)
        print("Local LLM Loaded")

    # Use Gemini
    else:
        LLM = genai.Client(api_key=GEMINI_KEY)

# --------------- NER Setup ---------------
# Load spaCy model
def load_spacy():

    global NLP
    NLP = spacy.load("en_core_web_sm")

    print("spaCy model loaded")
    return NLP

# -------------- MQTT Functions -------------

# Called when client connects to the broker
def on_connect(client, userdata, flags, rc):
    client.subscribe(MQTT_TOPIC)\
    
# Called when a message is received
def on_message(client, userdata, msg):

    global NLP

    # Decode MQTT message
    text = msg.payload.decode("utf-8")

    doc = NLP(text)
    reminder = {"Name" : "",            # Identified Target
                "Text" : "",            # Contents of reminder
                "Modified_Text" : ""}   # 2nd Person modification

    # Check for "me" first as a priority
    if re.search(r'\bme\b', text, re.IGNORECASE):
        reminder["Name"] = "me"

    else:
        # Use dependency parsing to extract the first PERSON name
        for token in doc:
            if token.ent_type_ == "PERSON" and token.dep_ in ("dobj", "pobj", "nsubj"):
                reminder["Name"] = token.text.lower()
                break

    # If no name or "me" detected
    if reminder["Name"] == "":
        reminder["Name"] = "None"

    print("Extracted:", reminder)

    # If 2nd person text transform is requested
    if APPLY_2ND_PERSON:

        print("Transforming Text")
        
        
        if LOCAL_ONLY: # Use PicoLLM

            # Generate response
            formatted_prompt = LOCAL_PROMPT.format(TEXT=text)
            response = LLM.generate(prompt=formatted_prompt,
                        completion_token_limit=64,
                        stop_phrases=["<|endoftext|>", "###", "##"])
            
            # Cleanup
            cleaned = response.completion.replace("<|endoftext|>", "").replace("<|assistant|>", "")
            cleaned = cleaned.replace("\n", " ").strip()  # Remove newlines and trim
            cleaned = re.sub(r"^[^a-zA-Z0-9]*", "", cleaned)  # Remove leading junk like "today?" or punctuation
            cleaned = re.sub(r'\s+', ' ', cleaned)  # Normalize spaces
            print("Cleaned response:", cleaned)

            # Save
            reminder["Modified_Text"] = cleaned
            insert_reminder(reminder)

        else: # Use Gemini
            formatted_prompt = GEMINI_PROMPT.format(TEXT=text)
            response = LLM.models.generate_content(
                model="gemini-2.0-flash", 
                contents=formatted_prompt)
            
            print("Cleaned response:", response.text)

            # Save
            reminder["Modified_Text"] = response.text
            insert_reminder(reminder)


# Setup MQTT
def load_MQTT():

    # Set up MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    # Start listening loop
    print(f"Listening on topic '{MQTT_TOPIC}'...")

    return client

#-------------- Main Function --------------
def main():

    try:
        create_table()
        load_spacy()
        load_LLM(LOCAL_ONLY)
        MQTT = load_MQTT()
        MQTT.loop_forever()

    except KeyboardInterrupt:
        print("Stopping, please wait...")

    finally:

        # Deallocate memory for LLM once program is terminated
        if LOCAL_ONLY:
            LLM.release()
    
if __name__ == '__main__':
    main()

