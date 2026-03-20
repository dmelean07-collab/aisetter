import json
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from memory import get_conversation, add_message, clear_conversation
from decision import get_stage, get_instruction

load_dotenv()

API_KEY = os.getenv("CLAUDE_API_KEY")
MODEL = "claude-haiku-4-5-20251001"
LOGS_FILE = "conversation_logs.json"


def load_persona(path="persona.json"):
    with open(path, "r") as f:
        return json.load(f)


def build_system_prompt(persona, stage, instruction):
    with open("brain.md", "r") as f:
        template = f.read()

    criteria_block = "\n".join(
        [f"- {c}" for c in persona.get("qualification_criteria", [])]
    )

    stage_instruction = f"Stage: {stage}\nInstruction: {instruction}"

    return template.format(
        owner_name=persona["owner_name"],
        business_name=persona["business_name"],
        target_audience=persona["target_audience"],
        specific_problem=persona["specific_problem"],
        specific_outcome=persona["specific_outcome"],
        owner_backstory=persona["owner_backstory"],
        qualification_criteria_block=criteria_block,
        booking_link=persona["booking_link"],
        stage_instruction=stage_instruction,
    )


# --- Conversation Logging (Pillar 4) ---

def _load_logs():
    if os.path.exists(LOGS_FILE):
        with open(LOGS_FILE, "r") as f:
            return json.load(f)
    return {}


def _save_logs(logs):
    with open(LOGS_FILE, "w") as f:
        json.dump(logs, f, indent=2)


def log_conversation(user_id, data: dict):
    """Update the log record for a lead. Call this at the end of a session."""
    logs = _load_logs()
    if user_id not in logs:
        logs[user_id] = {
            "lead_source": data.get("lead_source", "instagram_dm"),
            "first_message": data.get("first_message", ""),
            "first_contact_at": data.get("first_contact_at", datetime.utcnow().isoformat()),
            "response_time_seconds": data.get("response_time_seconds", 0),
        }
    logs[user_id].update({
        "last_updated": datetime.utcnow().isoformat(),
        "qualification_status": data.get("qualification_status", "pending"),
        "disqualification_reason": data.get("disqualification_reason", ""),
        "conversation_summary": data.get("conversation_summary", ""),
        "next_step": data.get("next_step", ""),
        "call_booked": data.get("call_booked", False),
        "call_datetime": data.get("call_datetime", ""),
        "lead_temperature": data.get("lead_temperature", "cold"),
        "notable_signals": data.get("notable_signals", ""),
    })
    _save_logs(logs)


def get_log(user_id):
    logs = _load_logs()
    return logs.get(user_id, {})


# --- Main Chat ---

def chat(user_id, user_message, persona_path="persona.json", lead_source="instagram_dm"):
    persona = load_persona(persona_path)

    history = get_conversation(user_id)

    # Track first message metadata
    is_first_message = len(history) == 0
    first_contact_at = datetime.utcnow().isoformat()

    stage = get_stage(history)
    instruction = get_instruction(stage)

    add_message(user_id, "user", user_message)
    history = get_conversation(user_id)

    formatted_messages = [
        {
            "role": msg["role"],
            "content": [{"type": "text", "text": msg["content"]}],
        }
        for msg in history
    ]

    system_prompt = build_system_prompt(persona, stage, instruction)

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": MODEL,
            "max_tokens": 300,
            "system": system_prompt,
            "messages": formatted_messages,
        },
    )

    data = response.json()

    if "content" in data:
        reply = data["content"][0]["text"]
        add_message(user_id, "assistant", reply)

        # Log first contact metadata
        if is_first_message:
            log_conversation(user_id, {
                "lead_source": lead_source,
                "first_message": user_message,
                "first_contact_at": first_contact_at,
                "qualification_status": "pending",
                "lead_temperature": "cold",
            })

        return reply
    else:
        return f"Error: {data}"


if __name__ == "__main__":
    user_id = "live_test"
    clear_conversation(user_id)
    print("Chat started. Type your messages. Ctrl+C to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            reply = chat(user_id, user_input)
            print(f"\nSetter: {reply}\n")
        except KeyboardInterrupt:
            print("\nDone.")
            break
