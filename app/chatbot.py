from openai import OpenAI

from app.config import (
    OPENROUTER_API_KEY,
    MODEL_NAME
)

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)


def ask_llm(messages):

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        max_tokens=300
    )

    return response.choices[0].message.content