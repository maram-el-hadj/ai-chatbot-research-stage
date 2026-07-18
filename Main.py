import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

print("=" * 50)
print("🤖 AI Chatbot")
print("Type 'exit' to quit.")
print("=" * 50)

while True:

    user = input("\nYou: ")

    if user.lower() == "exit":
        print("\n👋 Goodbye!")
        break

    response = client.chat.completions.create(
        model="deepseek/deepseek-chat-v3-0324",
        messages=[
    {
        "role": "system",
        "content": """
You are an AI assistant for a Research Center.

Rules:
- Be professional.
- Answer clearly.
- Be polite.
- If you don't know, say you don't know.
- Keep answers concise.
"""
    },
    {
        "role": "user",
        "content": user
    }
],
        max_tokens=300
    )

    # HEDHOM DAKHEL EL WHILE
    print(response)

    if response.choices:
        print("\nAssistant:", response.choices[0].message.content)
    else:
        print("No response received.")