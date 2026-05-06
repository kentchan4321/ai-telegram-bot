from flask import Flask, request
import requests
import os
import gspread
import json

from google.oauth2.service_account import Credentials
from datetime import datetime

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

    first_name = data["message"]["from"].get("first_name", "")
    last_name = data["message"]["from"].get("last_name", "")
    username = data["message"]["from"].get("username", "")

    user_name = (first_name + " " + last_name).strip()

    if username:
        user_name = user_name + " @" + username

    reply = ask_gpt(message)

    save_to_sheet(chat_id, user_name, message, reply)

    send_telegram(chat_id, reply)

    return "ok"

def ask_gpt(message):

    system_instruction = """
You are a customer service assistant for event vendor registration.

Event information:
Dragon Boat Vendor Event
Date: 16-21 June 2026
Time: 10:00am - 10:00pm
Location: Level G, The Starling Mall

Registration Link:
https://forms.gle/Eeh1UZv6EzJD8HnZ6

Social Media:
FB: Mylollipopmarket (MAC Event)
IG: mac_event_

Rules:
- Answer based only on the event information above
- Do not make up information
- Reply in the same language as the user
- Keep replies short, friendly, and human-like
- If the answer is not available, say:
Sorry, please contact support for more details.
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
        json={
            "chat_id": chat_id,
            "text": text
        },
        headers={
            "Content-Type": "application/json; charset=utf-8"
        }
    )

def save_to_sheet(chat_id, user_name, user_message, bot_reply):

    try:

        creds_json = os.environ.get("GOOGLE_CREDENTIALS")
        sheet_name = os.environ.get("GOOGLE_SHEET_NAME")

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        creds_dict = json.loads(creds_json)

        creds = Credentials.from_service_account_info(
            creds_dict,
            scopes=scopes
        )

        client = gspread.authorize(creds)

        sheet = client.open(sheet_name).sheet1

        sheet.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            str(chat_id),
            user_name,
            user_message,
            bot_reply
        ])

    except Exception as e:
        print("Google Sheet logging error:", e)
