from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# Initialize client
client = OpenAI(api_key=None)  

def generate_text(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
prompt = "Generate a short poem about the sea."

print(generate_text(prompt))
