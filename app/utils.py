from datetime import datetime, timezone
import pandas as pd

def now_utc_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat(
    )

def ensure_ohlcv_columns(df: pd.DataFrame):
    df = df.rename(columns={c: c.lower() for c in df.columns})
    needed = ["open","high","low","close","volume"]
    for n in needed:
        if n not in df.columns:
            raise ValueError(f"Missing column '{n}' in OHLCV data")
    if "time" not in df.columns:
        # try to derive from index
        try:
            df["time"] = pd.to_datetime(df.index)
        except Exception:
            df["time"] = pd.to_datetime("now")
    else:
        df["time"] = pd.to_datetime(df["time"])
    return df

def dropna_tail(df: pd.DataFrame, min_rows: int = 220):
    df = df.dropna()
    if len(df) < min_rows:
        raise ValueError(f"Not enough rows after dropping NaN: {len(df)} (need >= {min_rows})")
    return df

def yf_interval_map(iv: str) -> str:
    iv = iv.lower()
    return "60m" if iv == "1h" else iv