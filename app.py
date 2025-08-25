import os
import json
import requests
from flask import Flask, render_template, request, session, jsonify
from flask_session import Session
import openai
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "super-secret-demo-key"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

# Replace with your N8N webhook URL
N8N_WEBHOOK_URL = "https://mvalept-demos89.app.n8n.cloud/webhook-test/decision"


def call_openai(messages):
    """Call OpenAI chat completion with conversation history."""
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.4
    )
    return response.choices[0].message["content"]


def suggest_slots(num_days=5):
    """Generate 2 slots per day for the next num_days."""
    slots = []
    today = datetime.now()
    for i in range(1, num_days + 1):
        day = today + timedelta(days=i)
        for hour in [10, 15]:
            dt = day.replace(hour=hour, minute=0, second=0, microsecond=0)
            slots.append(dt.isoformat())
    return slots


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")

    if "history" not in session:
        session["history"] = [
            {"role": "system", "content": """You are 'HomeCare Agent', an appliance troubleshooting assistant. 
Your tasks:
- Understand appliance issues.
- Decide if booking a technician is needed.
- If NOT needed: suggest 2-3 safe troubleshooting steps.
- If booking IS needed OR user asks to book: propose 5 available slots (from backend).
- Collect missing details (name, email, address).
- Once user chooses a slot and info is complete, return structured JSON payload for booking."""}
        ]

    history = session["history"]
    history.append({"role": "user", "content": user_message})

    # If user explicitly confirms booking or chooses a slot
    if "book" in user_message.lower() or "slot" in user_message.lower():
        slots = suggest_slots()
        reply = "I can book a technician. Here are available slots:\n" + "\n".join(slots)
        history.append({"role": "assistant", "content": reply})
        session["history"] = history
        return jsonify({"reply": reply, "slots": slots})

    # Otherwise, let AI respond
    reply = call_openai(history)
    history.append({"role": "assistant", "content": reply})
    session["history"] = history
    return jsonify({"reply": reply})


@app.route("/book", methods=["POST"])
def book():
    data = request.json
    # Data includes: chosen_slot, appliance, description, user info
    booking_payload = {
        "appliance": data.get("appliance", "unknown"),
        "issue_summary": data.get("issue_summary", ""),
        "urgency": data.get("urgency", "normal"),
        "customer": {
            "name": data.get("name", ""),
            "email": data.get("email", ""),
            "phone": data.get("phone", ""),
            "address": data.get("address", "")
        },
        "chosen_slot": data.get("chosen_slot", ""),
        "description": data.get("description", "")
    }

    # Send to N8N webhook
    try:
        r = requests.post(N8N_WEBHOOK_URL, json=booking_payload, timeout=10)
        r.raise_for_status()
        return jsonify({"status": "success", "message": "✅ Booking sent to N8N", "payload": booking_payload})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
