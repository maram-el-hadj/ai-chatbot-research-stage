import json
import uuid
from pathlib import Path
from datetime import datetime

# ==========================================
# Configuration
# ==========================================

CHAT_DIR = Path("conversations")
CHAT_DIR.mkdir(exist_ok=True)


# ==========================================
# Create New Chat
# ==========================================

def create_chat(title="New Chat"):
    chat_id = str(uuid.uuid4())

    data = {
        "id": chat_id,
        "title": title,
        "created_at": datetime.now().isoformat(),
        "messages": []
    }

    save_chat(chat_id, data)

    return chat_id


# ==========================================
# Save Chat
# ==========================================

def save_chat(chat_id, data):
    path = CHAT_DIR / f"{chat_id}.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ==========================================
# Load Chat
# ==========================================

def load_chat(chat_id):

    path = CHAT_DIR / f"{chat_id}.json"

    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ==========================================
# List Chats
# ==========================================

def list_chats():

    chats = []

    for file in CHAT_DIR.glob("*.json"):

        with open(file, "r", encoding="utf-8") as f:

            data = json.load(f)

            chats.append(data)

    chats.sort(
        key=lambda x: x["created_at"],
        reverse=True
    )

    return chats


# ==========================================
# Delete Chat
# ==========================================

def delete_chat(chat_id):

    path = CHAT_DIR / f"{chat_id}.json"

    if path.exists():
        path.unlink()


# ==========================================
# Rename Chat
# ==========================================

def rename_chat(chat_id, new_title):

    data = load_chat(chat_id)

    if data:

        data["title"] = new_title

        save_chat(chat_id, data)


# ==========================================
# Append Message
# ==========================================

def add_message(chat_id, role, content):

    data = load_chat(chat_id)

    if data is None:
        return

    data["messages"].append({
        "role": role,
        "content": content
    })

    save_chat(chat_id, data)