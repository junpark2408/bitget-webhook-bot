import hmac
import hashlib
import time
import requests
import json
import os

# === Bitget API 인증 정보 ===
API_KEY = os.getenv("BITGET_API_KEY")
API_SECRET = os.getenv("BITGET_API_SECRET")
API_PASSPHRASE = os.getenv("BITGET_API_PASSPHRASE")
BASE_URL = "https://api.bitget.com"  # 실거래용

# === 시그니처 생성 함수 ===
def _generate_signature(timestamp, method, request_path, body):
    body_str = json.dumps(body) if body else ""
    message = f"{timestamp}{method}{request_path}{body_str}"
    signature = hmac.new(
        bytes(API_SECRET, "utf-8"),
        bytes(message, "utf-8"),
        hashlib.sha256
    ).hexdigest()
    return signature

# === Bitget 주문 요청 ===
def place_order(symbol, side, size, margin_mode="cross", leverage=5):
    timestamp = str(int(time.time() * 1000))
    method = "POST"
    path = "/api/mix/v1/order/placeOrder"
    url = BASE_URL + path

    # 주문 바디 구성
    body = {
        "symbol": symbol,
        "marginCoin": "USDT",
        "side": side,  # open_long, open_short, close_long, close_short
        "orderType": "market",
        "size": str(size),
        "marginMode": margin_mode,
        "leverage": str(leverage)
    }

    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": _generate_signature(timestamp, method, path, body),
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=body)
        res_data = response.json()

        if response.status_code == 200 and res_data.get("code") == "00000":
            print(f"✅ Order success: {side}, Size: {size}")
        else:
            print(f"❌ Order failed: {res_data}")
    except Exception as e:
        print(f"🔥 Error placing order: {e}")
