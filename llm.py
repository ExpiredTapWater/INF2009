import os
import picollm

pllm = picollm.create(
    access_key='${PICOVOICE_KEY}',
    model_path='./phi2-290.pllm')

res = pllm.generate('Rewrite this text to 3rd person: "Can you ask John to buy Eggs"')
print(res.completion)