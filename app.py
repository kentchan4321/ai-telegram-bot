from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    message = data['message']['text']
    chat_id = data['message']['chat']['id']

    reply = ask_gpt(message)

    send_telegram(chat_id, reply)
    return "ok"

def ask_gpt(message):
    url = "https://api.openai.com/v1/responses"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": "gpt-4o-mini",
        "input": message
    }
    r = requests.post(url, headers=headers, json=json_data)
    return r.json()["output_text"]

def send_telegram(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(
    url,
    json={"chat_id": chat_id, "text": text},
    headers={"Content-Type": "application/json; charset=utf-8"}
)
@app.route('/', methods=['GET'])
def home():
    return "Bot is running!"

if __name__ == "__main__":
    app.run()
