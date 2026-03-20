import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from setter import chat

load_dotenv()

app = Flask(__name__)

MANYCHAT_API_KEY = os.getenv("MANYCHAT_API_KEY")


def send_manychat_reply(subscriber_id, text):
    url = "https://api.manychat.com/fb/sending/sendContent"
    headers = {
        "Authorization": f"Bearer {MANYCHAT_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "subscriber_id": subscriber_id,
        "data": {
            "version": "v2",
            "content": {
                "messages": [{"type": "text", "text": text}]
            }
        },
        "message_tag": "NON_PROMOTIONAL_SUBSCRIPTION"
    }
    r = requests.post(url, json=payload, headers=headers)
    print(f"[manychat send] {r.status_code} {r.text}")
    return r


@app.route("/webhook", methods=["POST"])
def handle_message():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"status": "ok"}), 200

    print(f"[payload] {data}")

    subscriber_id = (
        data.get("id")
        or data.get("subscriber_id")
        or data.get("contact_id")
        or "unknown"
    )
    user_message = (
        data.get("last_text_input")
        or data.get("last_input_text")
        or data.get("message")
        or data.get("text")
        or ""
    ).strip()

    if not user_message:
        return jsonify({"status": "ok"}), 200

    print(f"[DM] from {subscriber_id}: {user_message}")

    reply = chat(
        user_id=str(subscriber_id),
        user_message=user_message,
        lead_source="instagram_dm",
    )

    print(f"[reply] {reply}")

    send_manychat_reply(subscriber_id, reply)

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
