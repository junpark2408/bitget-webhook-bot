from flask import Flask, request, jsonify
import datetime
from bitget_trading import place_order  # ✅ 실전 주문 함수 불러오기

app = Flask(__name__)

# 기본 설정
SYMBOL = "BTCUSDT"
FIXED_SIZE = 0.006  # 고정 포지션 크기
LEVERAGE = 5        # 고정 레버리지

def log_signal(signal_type):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] 📩 Received signal: {signal_type}")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if not data or 'signal' not in data:
        return jsonify({'status': 'error', 'message': 'Invalid payload'}), 400

    signal = data['signal']
    log_signal(signal)

    # ✅ 실제 주문 연결
    if signal == "go_long":
        place_order(SYMBOL, "open_long", FIXED_SIZE, leverage=LEVERAGE)
    elif signal == "go_short":
        place_order(SYMBOL, "open_short", FIXED_SIZE, leverage=LEVERAGE)
    elif signal == "exit_long_now":
        place_order(SYMBOL, "close_long", FIXED_SIZE, leverage=LEVERAGE)
    elif signal == "exit_short_now":
        place_order(SYMBOL, "close_short", FIXED_SIZE, leverage=LEVERAGE)
    elif signal == "ping":
        pass  # 핑은 서버 상태 확인용
    else:
        print("⚠️ Unknown signal")

    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
