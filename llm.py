import os
import picollm

pllm = picollm.create(
    access_key=os.getenv("PICOVOICE_KEY"),
    model_path='./phi2-290.pllm')

print("Running")
res = pllm.generate(prompt='Instruct: Rewrite the sentence to 2nd person: "Remind John to buy dinner on his way home"\nOutput:',
                    completion_token_limit=64,
                    stop_phrases=["\n","Exercise:"])
print(res.completion)