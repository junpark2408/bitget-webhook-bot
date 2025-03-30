from flask import Flask, request
import time, hmac, hashlib, json, requests, os

app = Flask(__name__)

API_KEY = os.getenv("BITGET_API_KEY")
API_SECRET = os.getenv("BITGET_API_SECRET")
API_PASSPHRASE = os.getenv("BITGET_API_PASSPHRASE")

SYMBOL = "BTCUSDT_UMCBL"
BASE_URL = "https://api.bitget.com"
LEVERAGE = 3

ENTRY_SIZES = {
    "entry_long_1": 0.006,
    "entry_long_2": 0.003,
    "entry_long_3": 0.003,
    "entry_long_4": 0.006,
    "entry_long_5": 0.009
}

total_position_size = 0.0

def get_headers(method, request_path, body=""):
    timestamp = str(int(time.time() * 1000))
    pre_hash = f"{timestamp}{method}{request_path}{body}"
    sign = hmac.new(API_SECRET.encode(), pre_hash.encode(), hashlib.sha256).hexdigest()
    return {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": sign,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "Content-Type": "application/json"
    }

def set_leverage():
    endpoint = "/api/mix/v1/account/setLeverage"
    body = {
        "symbol": SYMBOL,
        "marginCoin": "USDT",
        "leverage": str(LEVERAGE),
        "holdSide": "long"
    }
    headers = get_headers("POST", endpoint, json.dumps(body))
    response = requests.post(BASE_URL + endpoint, headers=headers, json=body)
    print("[레버리지 설정]", response.text)

def place_order(side, size):
    endpoint = "/api/mix/v1/order/placeOrder"
    body = {
        "symbol": SYMBOL,
        "marginCoin": "USDT",
        "size": str(size),
        "side": side,
        "orderType": "market",
        "productType": "umcbl"
    }
    headers = get_headers("POST", endpoint, json.dumps(body))
    response = requests.post(BASE_URL + endpoint, headers=headers, json=body)
    print(f"[주문 실행] {side} {size} BTC →", response.text)
    return response.json()

@app.route("/webhook", methods=["POST"])
def webhook():
    global total_position_size

    data = request.json
    print("[수신된 데이터]", data)
    msg = data.get("signal", "")

    if msg == "ping":
        print("[Ping] 서버 활성 상태 유지 확인")
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
    return "✅ Bitget Webhook Bot is Running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
