import hmac
import hashlib
import time
import requests
import json
import os

# 환경변수 또는 직접 입력 가능
API_KEY = os.getenv("BITGET_API_KEY")
API_SECRET = os.getenv("BITGET_API_SECRET")
API_PASSPHRASE = os.getenv("BITGET_API_PASSPHRASE")
BASE_URL = "https://api.bitget.com"

# Bitget 서명 생성 함수
def _generate_signature(timestamp, method, request_path, body):
    if body:
        body_str = json.dumps(body)
    else:
        body_str = ''
    
    message = f'{timestamp}{method}{request_path}{body_str}'
    signature = hmac.new(bytes(API_SECRET, 'utf-8'), bytes(message, 'utf-8'), hashlib.sha256).hexdigest()
    return signature

# 주문 함수 (롱/숏 공통)
def _place_order(symbol, side, size, margin_mode="cross", leverage=3):
    timestamp = str(int(time.time() * 1000))
    method = "POST"
    path = "/api/mix/v1/order/placeOrder"
    url = BASE_URL + path

    body = {
        "symbol": symbol,
        "marginCoin": "USDT",
        "side": side,  # "open_long" 또는 "open_short"
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

    response = requests.post(url, headers=headers, json=body)
    print("[Bitget 응답]", response.status_code, response.text)

# 포지션 종료 함수 (롱/숏 전량 청산)
def _close_position(symbol, side):
    timestamp = str(int(time.time() * 1000))
    method = "POST"
    path = "/api/mix/v1/order/closePosition"
    url = BASE_URL + path

    body = {
        "symbol": symbol,
        "marginCoin": "USDT",
        "marginMode": "cross",
        "side": side
    }

    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": _generate_signature(timestamp, method, path, body),
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=body)
    print("[Bitget 청산 응답]", response.status_code, response.text)

# 외부에서 호출하는 함수들
def place_long_order():
    _place_order("BTCUSDT", side="open_long", size=0.006)

def place_short_order():
    _place_order("BTCUSDT", side="open_short", size=0.006)

def close_long_order():
    _close_position("BTCUSDT", side="close_long")

def close_short_order():
    _close_position("BTCUSDT", side="close_short")
