import os
import picollm

pllm = picollm.create(
    access_key=os.getenv("PICOVOICE_KEY"),
    model_path='./phi2-290.pllm')

print("Running")
res = pllm.generate(prompt='Instruct: Rewrite the sentence to 1st person "Remind John to buy dinner on his way home"',
                    completion_token_limit=64)
print(res.completion)