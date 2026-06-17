import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("api_key")

client = OpenAI()

response = client.responses.create(
    model="gpt-4.1-mini",
    input="Hello! Explain Computer science in simple terms."
)

print(response.output_text)
