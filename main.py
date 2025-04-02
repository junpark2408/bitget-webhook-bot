from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# ===== 너가 만든 모듈 가져오기 (거래소 API만) =====
from bitget_trading import place_long_order, place_short_order, close_long_order, close_short_order

# ===== 중복 신호 방지 =====
latest_signal = None

@app.route('/', methods=['POST'])
def webhook():
    global latest_signal
    data = request.get_json()
    signal = data.get('signal')

    if not signal:
        return jsonify({'error': 'No signal provided'}), 400

    if signal == latest_signal:
        return jsonify({'status': 'ignored (duplicate signal)'}), 200

    latest_signal = signal

    # ===== 신호 처리 =====
    if signal == 'go_long':
        print("🚀 롱 진입 시그널 수신")
        place_long_order()
    elif signal == 'go_short':
        print("📉 숏 진입 시그널 수신")
        place_short_order()
    elif signal == 'exit_long_now':
        print("✅ 롱 포지션 청산 시그널 수신")
        close_long_order()
    elif signal == 'exit_short_now':
        print("✅ 숏 포지션 청산 시그널 수신")
        close_short_order()
    elif signal == 'ping':
        print("📡 Ping 수신: 서버 정상 작동 중 ✅")
    else:
        print(f"⚠️ 알 수 없는 시그널 수신: {signal}")
        return jsonify({'error': 'Unknown signal'}), 400

    return jsonify({'status': 'ok'})

# ===== Render 배포용 =====
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
