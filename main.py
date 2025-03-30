import os
import requests
from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# ====== 1. 텔레그램 설정 ======
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

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
entry_count = 0
last_entry_time = None

ENTRY_SIZES = {
    "long_1": 0.006,
    "long_2": 0.003,
    "long_3": 0.003,
    "long_4": 0.006,
    "long_5": 0.009,
}

HFT_ENTRY_SIZE = 0.006  # Sunil 전략 고정 진입 수량

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
    global total_position_size, entry_count, last_entry_time
    data = request.json
    msg = data.get("signal", "")

    if msg == "ping":
        print("[Ping] 서버 응답 OK")
        return {"status": "pong"}, 200

    # 기존 전략 진입 처리
    if msg in ENTRY_SIZES:
        size = ENTRY_SIZES[msg]
        set_leverage()
        total_position_size += size
        entry_count += 1
        last_entry_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
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
        entry_count = 0
        return place_order("close_long", exit_size)

    # 새로운 전략: Sunil HFT 전략 처리
    elif msg == "go_long":
        set_leverage()
        return place_order("open_long", HFT_ENTRY_SIZE)

    elif msg == "go_short":
        set_leverage()
        return place_order("open_short", HFT_ENTRY_SIZE)

    elif msg == "exit_long_now":
        return place_order("close_long", HFT_ENTRY_SIZE)

    elif msg == "exit_short_now":
        return place_order("close_short", HFT_ENTRY_SIZE)

    return {"error": "Invalid signal"}, 400

@app.route("/p", methods=["GET"])
def get_status():
    avg_price_usdt = round(total_position_size * 80000, 2)  # 예시: BTC 가격 80000
    summary = f"\ud83d\udcca 서버 상태 요약\n"
    summary += "\u2500" * 20 + "\n"
    summary += "\u2705 서버 작동 중\n"
    summary += f"\ud83d\udcc8 현재 진입 차수: {entry_count}차\n"
    summary += f"\ud83d\udcb0 누적 진입 수량: {round(total_position_size, 6)} BTC\n"
    summary += f"\ud83d\udcb5 누적 진입 금액: 약 {avg_price_usdt} USDT (BTC=80000 기준)\n"
    summary += f"\ud83d\udcc5 마지막 진입 시점: {last_entry_time if last_entry_time else '없음'}"
    send_telegram_message(summary)
    return {"status": "sent"}, 200

@app.route("/")
def home():
    return "\u2705 Bitget Webhook Bot is Running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
