import json
import os

MEMORY_FILE = "conversations.json"


def _load():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}


def _save(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_conversation(user_id):
    data = _load()
    return data.get(str(user_id), [])


def add_message(user_id, role, message):
    data = _load()
    uid = str(user_id)
    if uid not in data:
        data[uid] = []
    data[uid].append({"role": role, "content": message})
    _save(data)


def clear_conversation(user_id):
    data = _load()
    uid = str(user_id)
    if uid in data:
        del data[uid]
        _save(data)
