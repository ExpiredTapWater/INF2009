# ----------------- Import Stuff ------------------
import os
import re
import picollm
import spacy
import paho.mqtt.client as mqtt

# --------------- Setup Environment ---------------
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "pi/transcript"
LLM_PATH = './phi3.5-289.pllm'
KEY = os.getenv("PICOVOICE_KEY")
NLP = None
LLM = None
PROMPT = (
    "Rewrite the sentence as though you are relaying information to another person. Only output the rewritten sentence\n"
    "{TEXT}"
)
#"Rewrite the sentence in second person. Only output the rewritten sentence:\n"

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

    # Use dependency parsing to extract names more accurately
    for token in doc:
        if token.ent_type_ == "PERSON" and token.dep_ in ("dobj", "pobj", "nsubj"):
            name = token.text.lower()
            person_to_message[name] = text

    # Manually check for the word "me"
    if "me" in text.lower():
        person_to_message["me"] = text

    if person_to_message:
        print("Extracted:", person_to_message)
    else:
        print("No person detected.")

    print("Transforming text")
    formatted_prompt = PROMPT.format(TEXT=text)
    response = LLM.generate(prompt=formatted_prompt,
                            completion_token_limit=64,
                            stop_phrases=["<|endoftext|>", "###"])
    print(response.completion)

    cleaned = response.completion.replace("<|endoftext|>", "").replace("<|assistant|>", "")
    cleaned = cleaned.replace("\n", " ").strip()  # Remove newlines and trim
    cleaned = re.sub(r"^[^a-zA-Z0-9]*", "", cleaned)  # Remove leading junk like "today?" or punctuation
    cleaned = re.sub(r'\s+', ' ', cleaned)  # Normalize spaces
    print("Cleaned response:", cleaned)

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

    try:
        load_spacy()
        load_LLM()
        MQTT = load_MQTT()
        MQTT.loop_forever()

    except KeyboardInterrupt:
        print("Releasing Memory, please wait!")

    finally:
        LLM.release()
    
if __name__ == '__main__':
    main()
