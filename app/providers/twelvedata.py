from __future__ import annotations
import pandas as pd
from app.config import TWELVEDATA_API_KEY
from app.utils import ensure_ohlcv_columns

try:
    from twelvedata import TDClient
    _HAS_TD_SDK = True
except Exception:
    _HAS_TD_SDK = False
    import httpx

def _map_iv(iv: str) -> str:
    iv = iv.lower()
    return {
        "1m": "1min", "2m": "2min", "5m": "5min", "15m": "15min",
        "30m": "30min", "60m":"1h", "1h": "1h", "1d": "1day"
    }.get(iv, "1h")

def fetch_ohlcv(symbol: str, interval: str = "1h") -> pd.DataFrame:
    if not TWELVEDATA_API_KEY:
        raise RuntimeError("TWELVEDATA_API_KEY not set; put it in .env")
    
    td_iv = _map_iv(interval)

    # SDK path (preferred):
    if _HAS_TD_SDK:
        td = TDClient(apikey=TWELVEDATA_API_KEY)
        ts = td.time_series(symbol=symbol, interval=td_iv, outputsize=5000)
        df = ts.as_pandas()  # index is datetime, columns: open, high, low, close, volume
        if df is None or df.empty:
            raise RuntimeError("Twelve Data SDK returned no data")
        df = df.reset_index().rename(columns={"index":"time"})
        df = df[["time","open","high","low","close","volume"]]
        df["time"] = pd.to_datetime(df["time"])
        df = df.sort_values("time").reset_index(drop=True)
        return ensure_ohlcv_columns(df)
    
    # --- HTTP fallback (if SDK not installed) ---
    params = {
        "symbol": symbol,
        "interval": td_iv,
        "apikey": TWELVEDATA_API_KEY,
        "outputsize": 5000,
        "format": "JSON",
    }
    r = httpx.get("https://api.twelvedata.com/time_series", params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    if "values" not in data:
        raise RuntimeError(f"Twelve Data error: {data}")
    rows = data["values"]
    df = pd.DataFrame(rows).rename(columns={"datetime": "time"})
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)
    return ensure_ohlcv_columns(df)