import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ====== 1. 텔레그램 설정 ======
TELEGRAM_BOT_TOKEN = "<YOUR_TELEGRAM_BOT_TOKEN>"
TELEGRAM_CHAT_ID = "<YOUR_CHAT_ID>"

# ====== 2. 텔레그램 전송 함수 ======
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("텔레그램 전송 오류:", e)

# ====== 3. 서버 웹훅 엔드포인트 ======
total_position_size = 0.0
ENTRY_SIZES = {
    "long_1": 0.006,
    "long_2": 0.003,
    "long_3": 0.003,
    "long_4": 0.006,
    "long_5": 0.009,
}

def set_leverage():
    # 설정 예시: 레버리지 3배
    pass

def place_order(order_type, size):
    msg = f"{order_type.upper()} 주문 실행 - 수량: {size} BTC"
    print(msg)
    send_telegram_message(msg)
    return {"status": msg}, 200

@app.route("/webhook", methods=["POST"])
def webhook():
    global total_position_size
    data = request.json
    msg = data.get("signal", "")

    if msg == "ping":
        print("[Ping] 서버 응답 OK")
        send_telegram_message("✅ 서버 정상 작동 중 (ping 응답)")
        return {"status": "pong"}, 200

    if msg in ENTRY_SIZES:
        size = ENTRY_SIZES[msg]
        set_leverage()
        total_position_size += size
        return place_order("open_long", size)

    elif msg == "exit_long_5":
        return place_order("close_long", 0.009)

    elif msg == "partial_exit":
        exit_size = round(total_position_size * 0.5, 6)
        total_position_size -= exit_size
        return place_order("close_long", exit_size)

    elif msg == "full_exit":
        exit_size = total_position_size
        total_position_size = 0.0
        return place_order("close_long", exit_size)

    return {"error": "Invalid signal"}, 400

@app.route("/")
def home():
    return "\u2705 Bitget Webhook Bot is Running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
