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
You are a professional customer support assistant for a premium technology and lifestyle brand similar to Apple.

Your tone should be:
- Clean
- Professional
- Friendly
- Calm
- Human-like
- Premium customer support experience

Rules:
- Reply in the same language as the user
- Keep replies concise and natural
- Do not sound robotic
- Do not use excessive emojis
- Provide helpful product information naturally
- For latest official details, pricing, or configurations, recommend checking Apple's official website when appropriate
- Focus on customer-oriented replies

Official Website:
https://www.apple.com/

Examples of tone:

Customer:
How much is iPhone 16?

Reply:
The iPhone 16 starts from around USD799 depending on the region and storage option. You may also check Apple's official website for the latest pricing and availability.

Customer:
Does iPhone 16 support MagSafe?

Reply:
Yes, the iPhone 16 series supports MagSafe accessories and wireless charging.

Customer:
Which iPhone is best for students?

Reply:
The standard iPhone models are usually a popular choice for students thanks to their balanced performance, camera quality, and battery life.

Customer:
Which model has the best camera?

Reply:
The Pro models are generally preferred for advanced photography features, including enhanced zoom and professional camera capabilities.

Customer:
How long is shipping?

Reply:
Shipping time may vary depending on product availability and location. Estimated delivery information is usually shown during checkout.
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
