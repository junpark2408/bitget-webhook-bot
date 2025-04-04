import requests
import pandas as pd
from datetime import datetime
import time
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BITGET_API_URL = "https://api.bitget.com/api/v2/market/candles"

SYMBOLS = ["BTCUSDT", "ETHUSDT"]
TIMEFRAMES = {
    "5m": "5m",
    "15m": "15m",
    "1h": "1H",
    "4h": "4H"
}
EMA_PERIODS = [7, 30, 120, 240, 360]
last_alert_times = {}


def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=data)


def calculate_emas(df: pd.DataFrame) -> pd.DataFrame:
    for period in EMA_PERIODS:
        df[f'EMA_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
    return df


def fetch_ohlcv(symbol: str, timeframe: str, limit: int = 500):
    params = {
        "symbol": symbol,
        "granularity": timeframe,
        "limit": limit
    }
    response = requests.get(BITGET_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()["data"]
        df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume", "quoteVolume"])
        df = df.astype({
            "timestamp": "int64",
            "open": "float",
            "high": "float",
            "low": "float",
            "close": "float",
            "volume": "float",
            "quoteVolume": "float"
        })
        df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.sort_values("datetime", inplace=True)
        return df
    return None


def is_bullish(emas):
    return all(emas[i] > emas[i + 1] for i in range(len(emas) - 1))


def is_bearish(emas):
    return all(emas[i] < emas[i + 1] for i in range(len(emas) - 1))


def analyze_market():
    now = datetime.utcnow()
    for symbol in SYMBOLS:
        for label, tf in TIMEFRAMES.items():
            df = fetch_ohlcv(symbol, tf)
            if df is None or len(df) < max(EMA_PERIODS) + 5:
                continue

            df = calculate_emas(df)
            latest = df.iloc[-1]
            previous = df.iloc[-2]

            current_emas = [latest[f'EMA_{p}'] for p in EMA_PERIODS]
            previous_emas = [previous[f'EMA_{p}'] for p in EMA_PERIODS]

            key = f"{symbol}_{label}"

            just_bullish = is_bullish(current_emas) and not is_bullish(previous_emas)
            just_bearish = is_bearish(current_emas) and not is_bearish(previous_emas)

            should_alert = False
            if just_bullish or just_bearish:
                should_alert = True
            elif key not in last_alert_times or (now - last_alert_times[key]).total_seconds() > 3600:
                should_alert = True

            if should_alert:
                if just_bullish:
                    msg = f"\ud83d\udfe2 *\uac11 \uc815\ubc30\uc5f4 \uac10\uc9c0*\n\uc2ec\ubc88: {symbol}\n\ud0c0\uc784\ud504\ub808\uc784: {label}\n\uc2dc\uac04: {latest['datetime']}"
                    send_telegram_message(msg)
                    last_alert_times[key] = now
                elif just_bearish:
                    msg = f"\ud83d\udd34 *\uac11 \uc5ed\ubc30\uc5f4 \uac10\uc9c0*\n\uc2ec\ubc88: {symbol}\n\ud0c0\uc784\ud504\ub808\uc784: {label}\n\uc2dc\uac04: {latest['datetime']}"
                    send_telegram_message(msg)
                    last_alert_times[key] = now


if __name__ == "__main__":
    while True:
        try:
            analyze_market()
            time.sleep(60)  # 1\ubd84 \ub9e4 \uc2e4\ud589
        except Exception as e:
            send_telegram_message(f"\u26a0\ufe0f \uc5d0\ub7ec \ubc1c\uc0dd: {str(e)}")
            time.sleep(60)
