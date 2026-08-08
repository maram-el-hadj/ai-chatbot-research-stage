from openai import OpenAI

from config import (
    OPENROUTER_API_KEY,
    BASE_URL,
    MODEL_NAME,
    TEMPERATURE,
    MAX_TOKENS,
)


# ==========================================
# OpenRouter Client
# ==========================================

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=BASE_URL
)


# ==========================================
# Stream Answer
# ==========================================

def stream_answer(messages):
    """
    Stream the AI response token by token
    from OpenRouter.

    Yields small chunks of text as they arrive.
    """

    if not messages:
        raise ValueError(
            "No messages were provided."
        )

    stream = client.chat.completions.create(

        model=MODEL_NAME,

        messages=messages,

        temperature=TEMPERATURE,

        max_tokens=MAX_TOKENS,

        stream=True
    )

    for chunk in stream:

        if not chunk.choices:
            continue

        delta = chunk.choices[0].delta

        if delta is None:
            continue

        content = delta.content

        if content:
            yield content


# ==========================================
# Get Complete Response
# ==========================================

def get_streamed_answer(messages):
    """
    Stream the response and return
    the complete generated answer.

    Returns:
        str: complete AI response
    """

    full_response = ""

    for chunk in stream_answer(messages):

        full_response += chunk

    return full_response