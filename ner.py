from optimum.onnxruntime import ORTModelForTokenClassification
from transformers import AutoTokenizer, pipeline


print("Import ok")

tokenizer = AutoTokenizer.from_pretrained("laiyer/bert-base-NER-onnx")
model = ORTModelForTokenClassification.from_pretrained("laiyer/bert-base-NER-onnx")
ner = pipeline(
    task="ner",
    model=model,
    tokenizer=tokenizer,
)

print("Pipeline ok")

ner_output = ner("My name is John Doe.")
print(ner_output)