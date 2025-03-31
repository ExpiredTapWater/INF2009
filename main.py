# ----------------- Import Stuff ------------------
import os
import picollm
import spacy
import paho.mqtt.client as mqtt

# --------------- Setup Environment ---------------
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "pi/transcript"
LLM_PATH = "./phi2-290.pllm"
KEY = os.getenv("PICOVOICE_KEY")
NLP = None
LLM = None
SYS_PROMPT = "Rewrite this message to be from the recipient perspective:"

# Called when client connects to the broker
def on_connect(client, userdata, flags, rc):
    client.subscribe(MQTT_TOPIC)

# Called when a message is received
def on_message(client, userdata, msg):

    global NLP
    text = msg.payload.decode("utf-8")
    print(f"Received message: {text}")

    doc = NLP(text)
    person_to_message = {}

    # Extract named persons from spaCy
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text.lower()
            person_to_message[name] = text

    # Manually check for the word "me"
    if "me" in text.lower():
        person_to_message["me"] = text

    if person_to_message:
        print("Extracted:", person_to_message)
    else:
        print("No person detected.")

    # TEST CODE
    formatted_prompt = f"{SYS_PROMPT} '{text}'"
    response = LLM.generate(prompt=formatted_prompt)
    print(response.completion)

# Load spaCy model
def load_spacy():

    global NLP
    NLP = spacy.load("en_core_web_sm")

    print("spaCy model loaded")
    return NLP

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

def load_LLM():

    global LLM
    print(f"Loading LLM from: {LLM_PATH}")

    LLM = picollm.create(
    access_key=KEY,
    model_path=LLM_PATH
    )

    print("Model Loaded")

def main():

    load_spacy()
    load_LLM()
    MQTT = load_MQTT()
    MQTT.loop_forever()
    
if __name__ == '__main__':
    main()
