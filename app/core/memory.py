from app.core.prompts import SYSTEM_PROMPT
from app.examples import EXAMPLES

messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]

messages.extend(EXAMPLES)