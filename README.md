# LLM‑Assisted Trading Signal Agent

**Paper‑trading only. Not financial advice.**  
A FastAPI service + CLI that:
- Pulls OHLCV candles (Yahoo Finance by default; Twelve Data optional).
- Computes RSI, MACD, Bollinger Bands, ATR, and simple candlestick patterns (engulfing, doji).
- Summarizes recent headlines and classifies sentiment with GPT.
- Returns **long/short decision**, stop‑loss & take‑profit using ATR, plus an **explainable rationale**.

## Quickstart

```bash
# 1) Create venv and install deps
python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt

# 2) Configure environment (keys optional but recommended)
cp .env.example .env
# Edit .env and set OPENAI_API_KEY (and optionally TWELVEDATA_API_KEY / FINNHUB_API_KEY)

# 3) Run API
uvicorn app.main:app --reload --port 8000

# 4) Test:
```
http://127.0.0.1:8000/signal?symbol=BTC-USD&interval=1h
http://127.0.0.1:8000/signal?symbol=AAPL&interval=1h
```

CLI:
```bash
python -m app.cli --symbol BTC-USD --interval 1h --provider twelvedata
```


## Simple Output (default)
The API and CLI now return a compact payload so it's easy to act on:
```json
{
  "signal": "buy",
  "side": "long",
  "entry_price": 64512.34,
  "take_profit": 65988.45,
  "stop_loss": 63610.22,
  "confidence": 0.72,
  "reason": "buy due to trend moderate (ADX 21.4); RSI 29.8 oversold; bullish_engulfing; news neutral."
}
```