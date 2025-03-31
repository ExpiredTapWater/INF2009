import spacy
import paho.mqtt.client as mqtt

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# MQTT settings
MQTT_BROKER = "localhost"       # Replace with your broker IP if not local
MQTT_PORT = 1883
MQTT_TOPIC = "pi/transcript"

# Called when client connects to the broker
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code", rc)
    client.subscribe(MQTT_TOPIC)

# Called when a message is received
def on_message(client, userdata, msg):
    text = msg.payload.decode("utf-8")
    print(f"Received message: {text}")

    doc = nlp(text)
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


# Set up MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Start listening loop
print(f"Listening on topic '{MQTT_TOPIC}'...")
client.loop_forever()
