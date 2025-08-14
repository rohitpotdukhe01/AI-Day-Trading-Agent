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

# 4) Try it
curl "http://127.0.0.1:8000/signal?symbol=BTC-USD&interval=1h&provider=yahoo"
curl "http://127.0.0.1:8000/signal?symbol=AAPL&interval=1h&provider=yahoo"
```

## CLI
```bash
python -m app.cli --symbol BTC-USD --interval 1h --provider yahoo
```

## Notes
- **Yahoo Finance (`yfinance`)** is great to prototype: intraday can be delayed and limited.  
- **Twelve Data** gives real-time candles (requires API key).  
- **News**: Finnhub if key is set, else Yahoo news fallback.  
- Indicators via `pandas-ta`. Candlestick patterns implemented in pure pandas (no TA‑Lib build headaches).
- All outputs are for **education/paper trading**. Do your own research; markets are risky.

## Example Response
```json
{
  "symbol": "BTC-USD",
  "interval": "1h",
  "as_of": "2025-08-15T12:45:00Z",
  "decision": "long",
  "confidence": 0.62,
  "risk": {
    "atr": 325.8,
    "stop_loss": 62812.4,
    "take_profit": 65690.1,
    "direction": "long"
  },
  "why": {
    "ta": {"rsi": 34.9, "macd_hist": -12.1, "bb_pos": "lower_band_zone"},
    "patterns": ["bullish_engulfing"],
    "news": {"sentiment": "neutral", "confidence": 0.55, "top_headlines": ["...","..."]},
    "rules_fired": ["rsi_oversold", "near_lower_band", "bullish_engulfing"]
  }
}
```