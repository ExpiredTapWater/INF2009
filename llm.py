import os
import picollm

pllm = picollm.create(
    access_key=os.getenv("PICOVOICE_KEY"),
    model_path='./phi2-290.pllm')

print("Running")
res = pllm.generate(prompt='Rewrite the sentence to 2nd person: Remind John to buy dinner on his way home',
                    completion_token_limit=64,
                    stop_phrases=["Exercise:"])
print(res.completion)