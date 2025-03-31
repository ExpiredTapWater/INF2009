import os
import picollm

pllm = picollm.create(
    access_key=os.getenv("PICOVOICE_KEY"),
    model_path='./phi2-290.pllm')

res = pllm.generate(prompt='Rewrite in 3rd person: Remind John to buy dinner on his way home',
                    completion_token_limit=64)
print(res.completion)