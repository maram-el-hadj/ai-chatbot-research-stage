from app.core.session import add_message, clear_session, messages
from app.services.chatbot import ask_llm

print("=" * 50)
print("🤖 Research Assistant Chatbot")
print("Type 'clear' to reset memory | 'exit' to quit")
print("=" * 50)

while True:
    user = input("\nYou: ").strip()

    if not user:
        continue

    # Handle exit command
    if user.lower() == "exit":
        print("\n👋 Goodbye!")
        break

    # Handle clear command
    if user.lower() == "clear":
        clear_session()
        print("\n🧹 Memory reset successfully!")
        continue

    # Add user input to memory
    add_message("user", user)

    # Get assistant response
    assistant = ask_llm(messages)

    # Add assistant response to memory
    add_message("assistant", assistant)

    print("\nAssistant:", assistant)