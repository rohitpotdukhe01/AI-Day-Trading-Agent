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
    # --- SDK path (preferred) ---
    if _HAS_TD_SDK:
        td = TDClient(apikey=TWELVEDATA_API_KEY)
        ts = td.time_series(symbol=symbol, interval=td_iv, outputsize=5000)
        df = ts.as_pandas()  # index = DatetimeIndex; columns = open, high, low, close, volume (varies in case)
        if df is None or df.empty:
            raise RuntimeError("Twelve Data SDK returned no data")

        # Capture index name BEFORE reset_index (often 'datetime' or None)
        idx_name = df.index.name or "index"
        df = df.reset_index()

        # Normalize time column name to 'time'
        rename_map = {idx_name: "time", "datetime": "time", "Datetime": "time"}
        df = df.rename(columns=rename_map)

        # Normalize OHLCV column names to lowercase and ensure presence
        df.columns = [c.lower() for c in df.columns]
        # Sometimes SDK returns strings; coerce to numeric
        for c in ["open", "high", "low", "close", "volume"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")

        # Ensure time is datetime64[ns, UTC] or naive datetime (either is fine for our pipeline)
        if "time" not in df.columns:
            # fallback: try to find a datetime-like column
            for candidate in ["datetime", "date"]:
                if candidate in df.columns:
                    df = df.rename(columns={candidate: "time"})
                    break
        df["time"] = pd.to_datetime(df["time"], errors="coerce")

        # Keep only needed columns, sorted by ascending time
        df = df[["time", "open", "high", "low", "close", "volume"]].dropna(subset=["time"])
        df = df.sort_values("time").reset_index(drop=True)

        return ensure_ohlcv_columns(df)