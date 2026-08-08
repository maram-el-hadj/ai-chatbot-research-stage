import json
import uuid
from pathlib import Path
from datetime import datetime


# =========================================================
# CONFIGURATION
# =========================================================

CHAT_DIR = Path("conversations")
CHAT_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# CREATE NEW CHAT
# =========================================================

def create_chat(title="New Chat"):

    chat_id = str(uuid.uuid4())

    data = {
        "id": chat_id,
        "title": title,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "messages": []
    }

    save_chat(chat_id, data)

    return chat_id


# =========================================================
# SAVE CHAT
# =========================================================

def save_chat(chat_id, data=None):

    """
    Save a chat to conversations/<chat_id>.json

    If data is not provided, the existing chat is loaded
    and saved again.
    """

    if data is None:

        data = load_chat(chat_id)

        if data is None:
            return False

    data["updated_at"] = datetime.now().isoformat()

    path = CHAT_DIR / f"{chat_id}.json"

    try:

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

        return True

    except Exception:

        return False


# =========================================================
# LOAD CHAT
# =========================================================

def load_chat(chat_id):

    path = CHAT_DIR / f"{chat_id}.json"

    if not path.exists():
        return None

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception:

        return None


# =========================================================
# LIST ALL CHATS
# =========================================================

def list_chats():

    chats = []

    for file in CHAT_DIR.glob("*.json"):

        try:

            with open(
                file,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            chats.append(data)

        except Exception:

            # Ignore corrupted chat files
            continue

    chats.sort(
        key=lambda x: x.get(
            "updated_at",
            x.get(
                "created_at",
                ""
            )
        ),
        reverse=True
    )

    return chats


# =========================================================
# DELETE CHAT
# =========================================================

def delete_chat(chat_id):

    path = CHAT_DIR / f"{chat_id}.json"

    if path.exists():

        try:

            path.unlink()

            return True

        except Exception:

            return False

    return False


# =========================================================
# RENAME CHAT
# =========================================================

def rename_chat(
    chat_id,
    new_title
):

    data = load_chat(chat_id)

    if data is None:
        return False

    data["title"] = new_title.strip()

    return save_chat(
        chat_id,
        data
    )


# =========================================================
# ADD MESSAGE
# =========================================================

def add_message(
    chat_id,
    role,
    content
):

    data = load_chat(chat_id)

    if data is None:
        return False

    data.setdefault(
        "messages",
        []
    )

    data["messages"].append(
        {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
    )

    return save_chat(
        chat_id,
        data
    )


# =========================================================
# GET CHAT MESSAGES
# =========================================================

def get_messages(chat_id):

    data = load_chat(chat_id)

    if data is None:
        return []

    return data.get(
        "messages",
        []
    )


# =========================================================
# CLEAR CHAT MESSAGES
# =========================================================

def clear_messages(chat_id):

    data = load_chat(chat_id)

    if data is None:
        return False

    data["messages"] = []

    return save_chat(
        chat_id,
        data
    )