# ─────────────────────────────────────────
#  OIL TERMINAL · data/price_feed.py
#  Fetches live WTI & Brent data via yfinance
# ─────────────────────────────────────────

import yfinance as yf
import pandas as pd
import streamlit as st
from config import TICKER_WTI, TICKER_BRENT, INTERVAL, PERIOD


@st.cache_data(ttl=60)  # Cache for 60 seconds, then auto-refresh
def get_ohlcv(ticker: str) -> pd.DataFrame:
    """
    Fetch OHLCV candlestick data for a given ticker.
    Returns cleaned DataFrame with datetime index.
    """
    try:
        df = yf.download(
            ticker,
            period=PERIOD,
            interval=INTERVAL,
            auto_adjust=True,
            progress=False
        )
        if df.empty:
            return pd.DataFrame()

        df.index = pd.to_datetime(df.index)
        df.index = df.index.tz_localize(None)  # Remove timezone for clean display
        df.dropna(inplace=True)
        return df

    except Exception as e:
        st.error(f"Data fetch error for {ticker}: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=60)
def get_current_price(ticker: str) -> dict:
    """
    Returns current price, previous close, change, change %.
    """
    try:
        tk = yf.Ticker(ticker)
        info = tk.fast_info

        current  = round(float(info.last_price), 2)
        prev     = round(float(info.previous_close), 2)
        change   = round(current - prev, 2)
        change_p = round((change / prev) * 100, 2) if prev else 0.0

        return {
            "price"    : current,
            "prev"     : prev,
            "change"   : change,
            "change_p" : change_p,
        }
    except Exception:
        return {
            "price"    : 0.0,
            "prev"     : 0.0,
            "change"   : 0.0,
            "change_p" : 0.0,
        }


def get_volume_summary(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"current": 0, "avg": 0}

    try:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        vol = df["Volume"].dropna()
        vol_current = int(vol.iloc[-1]) if not vol.empty else 0
        vol_avg     = int(vol.mean())   if not vol.empty else 0
    except Exception:
        vol_current, vol_avg = 0, 0

    return {"current": vol_current, "avg": vol_avg}
