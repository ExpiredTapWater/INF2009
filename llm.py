import os
import picollm

pllm = picollm.create(
    access_key=os.getenv("PICOVOICE_KEY"),
    model_path='./phi2-290.pllm')

res = pllm.generate('How are you?')
print(res.completion)