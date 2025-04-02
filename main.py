//@version=6
strategy("Junhyeong High-Frequency Strategy - FAKE + Ping", overlay=true)

// === MACD & RSI 기반 시그널 ===
[macdLine, signalLine, _] = ta.macd(close, 12, 26, 9)
rsi = ta.rsi(close, 14)

longCondition  = ta.crossover(macdLine, signalLine) and rsi < 70
shortCondition = ta.crossunder(macdLine, signalLine) and rsi > 30

// === 시그널 조건 기반 알람 ===
alertcondition(longCondition, title="Go Long", message='{"signal":"go_long"}')
alertcondition(shortCondition, title="Go Short", message='{"signal":"go_short"}')
alertcondition(strategy.position_size > 0 and rsi > 80, title="Exit Long", message='{"signal":"exit_long_now"}')
alertcondition(strategy.position_size < 0 and rsi < 20, title="Exit Short", message='{"signal":"exit_short_now"}')

// === Ping 조건 (항상 true) ===
ping = true
alertcondition(ping, title="Ping Signal", message='{"signal":"ping"}')
