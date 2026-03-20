import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from setter import chat

load_dotenv()

app = Flask(__name__)


# ManyChat sends a POST to this endpoint with the subscriber's message.
# We call chat(), then return the reply in ManyChat's response format
# so ManyChat sends it back to the DM automatically.
@app.route("/webhook", methods=["POST"])
def handle_message():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "no data"}), 400

    # Print full payload so we can see exactly what ManyChat sends
    print(f"[payload] {data}")

    # Try every field name ManyChat might use
    subscriber_id = (
        data.get("subscriber_id")
        or data.get("contact_id")
        or data.get("id")
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
        return jsonify({"error": "no message"}), 400

    print(f"[DM] from {subscriber_id}: {user_message}")

    reply = chat(
        user_id=subscriber_id,
        user_message=user_message,
        lead_source="instagram_dm",
    )

    print(f"[reply] {reply}")

       # ManyChat reads this response and sends the text back to the subscriber
    return jsonify({
        "version": "v2",
        "content": {
            "messages": [
                {
                    "type": "text",
                    "text": reply
                }
            ],
            "actions": [],
            "quick_replies": []
        }
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

