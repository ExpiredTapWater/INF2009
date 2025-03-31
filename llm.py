import os
import picollm

pllm = picollm.create(
    access_key=os.getenv("PICOVOICE_KEY"),
    model_path='./phi2-290.pllm')

res = pllm.generate('Rewrite this message to be from the recipient perspective: "Can you remind John to buy dinner on his way home"')
print(res.completion)