from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

@app.route("/", methods=["POST"])
def webhook():
    data = request.json

    message = data["message"]["text"]
    chat_id = data["message"]["chat"]["id"]

    reply = ask_gpt(message)
    send_telegram(chat_id, reply)

    return "ok"

def ask_gpt(message):
    system_instruction = """
You are a customer service assistant of event.

Here is the event information:
Dragon Boat Vendor Event
Date: 16–21 June 2026
Time: 10:00am – 10:00pm
Location: Level G, The Starling Mall
Registration: https://forms.gle/Eeh1UZv6EzJD8HnZ6
Social: FB Mylollipopmarket (MAC Event), IG: mac_event_
Rental price :  Red Zone RM 1,680- Facing Shoplot
Orange Zone RM 1,500- Facing Walkway

Your task:
Answer the user question based on the information above. 
"""

    url = "https://api.openai.com/v1/responses"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": "gpt-4o-mini",
        "input": system_instruction + "\n\nUser message: " + message
    }

    r = requests.post(url, headers=headers, json=json_data)
    data = r.json()

    return data["output"][0]["content"][0]["text"]
"""

    url = "https://api.openai.com/v1/responses"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": "gpt-4o-mini",
        "input": system_instruction + "\n\nUser message: " + message
    }

    r = requests.post(url, headers=headers, json=json_data)
    data = r.json()

    return data["output"][0]["content"][0]["text"]

def send_telegram(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(
        url,
        json={"chat_id": chat_id, "text": text},
        headers={"Content-Type": "application/json; charset=utf-8"}
    )
