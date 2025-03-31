import os
from google import genai

KEY = os.getenv("GEMINI_KEY")
client = genai.Client(api_key=KEY)

response = client.models.generate_content(
    model="gemini-2.0-flash", contents="Explain how AI works in a few words"
)
print(response.text)