import os
import picollm

pllm = picollm.create(
    access_key=os.getenv("PICOVOICE_KEY"),
    model_path='./phi2-290.pllm')

print("Running")
res = pllm.generate(prompt='Instruct: Rewrite the sentence to 2nd person: "Remind John to buy dinner on his way home"\nOutput:',
                    completion_token_limit=64,
                    stop_phrases=["Exercise:"])
print(res.completion)

prompt = (
    "### Instruction:\n"
    "Rewrite the following sentence to 2nd person.\n"
    "### Input:\n"
    "Remind John to buy dinner on his way home.\n"
    "### Output:"
)
res = pllm.generate(prompt=prompt,
                    completion_token_limit=64,
                    stop_phrases=["Exercise:"])
print(res.completion)