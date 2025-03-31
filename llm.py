import os
import picollm

pllm = picollm.create(
    access_key=os.getenv("PICOVOICE_KEY"),
    model_path='./phi2-290.pllm')

print("Running 1")
res = pllm.generate(prompt='What is the intent here: Remind John to buy dinner on his way home',
                    completion_token_limit=64)
print(res.completion)

print("Running 2")
res = pllm.generate(prompt='Rewrite in 1st person: Remind John to buy dinner on his way home',
                    completion_token_limit=64)
print(res.completion)