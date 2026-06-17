from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

prompt = input("Enter your prompt: ")

client = OpenAI(api_key=api_key)
response = client.chat.completions.create(
  model="gpt-4.1-mini",
  messages=[
    {"role":"system","content":"I'M Emo Ai your professional assistant. I will help you with your coding tasks."},
    {"role":"user","content":f"{prompt}"}
  ]
)
print(response.choices[0].message.content)
