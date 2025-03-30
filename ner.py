import spacy

nlp = spacy.load("en_core_web_sm")
doc = nlp("Ask John to buy eggs")

for ent in doc.ents:
    print(ent.text, ent.label_)