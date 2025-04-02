from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

# 로그 출력 함수
def log_signal(signal_type):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] 📩 Received signal: {signal_type}")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if not data or 'signal' not in data:
        return jsonify({'status': 'error', 'message': 'Invalid payload'}), 400

    signal = data['signal']

    # 시그널에 따라 로그 출력
    if signal == "go_long":
        log_signal("Go Long ✅")
    elif signal == "go_short":
        log_signal("Go Short ✅")
    elif signal == "exit_long_now":
        log_signal("Exit Long Now 🔴")
    elif signal == "exit_short_now":
        log_signal("Exit Short Now 🔵")
    elif signal == "ping":
        log_signal("Ping 🟡 (heartbeat)")
    else:
        log_signal(f"Unknown Signal ❓: {signal}")

    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
