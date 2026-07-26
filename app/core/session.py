from app.core.prompts import SYSTEM_PROMPT

# Maximum number of messages to retain (including system prompt)
MAX_HISTORY = 10

# Initialize global conversation memory with system prompt
messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]

def add_message(role, content):
    """Adds a message to history and maintains MAX_HISTORY limit."""
    messages.append({
        "role": role,
        "content": content
    })

    # Keep System Prompt (index 0) intact, delete oldest conversation message (index 1)
    if len(messages) > MAX_HISTORY:
        del messages[1]


def clear_session():
    """Resets memory back to initial state with only the System Prompt."""
    global messages
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]