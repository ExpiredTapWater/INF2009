import onnxruntime
import numpy as np
from transformers import AutoTokenizer

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained("laiyer/bert-base-NER-onnx")

# Tokenize input
text = "My name is John Doe."
inputs = tokenizer(text, return_tensors="np", truncation=True)

# Load ONNX model
session = onnxruntime.InferenceSession("model.onnx")

# Run inference
outputs = session.run(None, {
    "input_ids": inputs["input_ids"],
    "attention_mask": inputs["attention_mask"]
})

# Get logits
logits = outputs[0]
predictions = np.argmax(logits, axis=-1)[0]

# Map back to tokens and labels
tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])

# You’ll need label mapping (usually in model config or README)
id2label = {
    0: "O",
    1: "B-PER",
    2: "I-PER",
    3: "B-ORG",
    4: "I-ORG",
    5: "B-LOC",
    6: "I-LOC"
}

for token, pred in zip(tokens, predictions):
    label = id2label.get(pred, "O")
    if label != "O":
        print(f"{token}: {label}")
