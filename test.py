from decision import get_stage, get_instruction
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("CLAUDE_API_KEY")

def ask_claude(message):
    # Load brain
    with open("brain.md", "r") as f:
        system_prompt = f.read()

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        json={
            "model": "claude-3-haiku-20240307",
            "max_tokens": 200,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": message}
                    ]
                }
            ]
        }
    )

    data = response.json()

    if "content" in data:
        return data["content"][0]["text"]
    else:
        return f"Error: {data}"

# Test
from memory import get_conversation, add_message

def chat(user_id, user_message):
    history = get_conversation(user_id)
    stage = get_stage(history)
    instruction = get_instruction(stage)

    # Add user message
    add_message(user_id, "user", user_message)

    # Format messages for Claude
    formatted_messages = []

    for msg in history:
        formatted_messages.append({
            "role": msg["role"],
            "content": [
                {"type": "text", "text": msg["content"]}
            ]
        })

    # Load brain
    with open("brain.md", "r") as f:
        system_prompt = f.read()

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        json={
            "model": "claude-3-haiku-20240307",
            "max_tokens": 200,
            "system": system_prompt + "\n\nCURRENT INSTRUCTION: " + instruction,
            "messages": formatted_messages
        }
    )

    data = response.json()

    if "content" in data:
        reply = data["content"][0]["text"]
        add_message(user_id, "assistant", reply)
        return reply
    else:
        return f"Error: {data}"
    
print(chat("user1", "Hey, I’ve been struggling to get clients"))
print(chat("user1", "I tried ads but they didn’t work"))
print(chat("user1", "I’m not sure if this is for me"))
print(chat("user1", "How much does it cost?"))