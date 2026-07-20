from app.memory import messages
from app.chatbot import ask_llm

print("=" * 50)
print("🤖 Research Assistant Chatbot")
print("Type 'exit' to quit.")
print("=" * 50)

while True:

    user = input("\nYou: ")

    if user.lower() == "exit":
        print("\n👋 Goodbye!")
        break

    messages.append(
        {
            "role": "user",
            "content": user
        }
    )

    assistant = ask_llm(messages)

    messages.append(
        {
            "role": "assistant",
            "content": assistant
        }
    )

    print("\nAssistant:", assistant)