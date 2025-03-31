import os
import picollm

pllm = picollm.create(
    access_key=os.getenv("PICOVOICE_KEY"),
    model_path='./phi3.5-289.pllm')

prompt1='Rewrite the sentence to 2nd person: Remind John to buy dinner on his way home'
prompt2 = (
    "Rewrite the sentence in second person. Only output the rewritten sentence:\n"
    "Remind John to buy dinner on his way home.\n"
)

print("Running")
res = pllm.generate(prompt=prompt2,
                    completion_token_limit=64)
print(res.completion)