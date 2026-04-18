# ─────────────────────────────────────────
#  OIL TERMINAL · config.py
#  Central settings — change values here
# ─────────────────────────────────────────

# Asset
TICKER_WTI   = "CL=F"       # WTI Crude Oil Futures
TICKER_BRENT = "BZ=F"       # Brent Crude Oil Futures

# Chart timeframe
INTERVAL     = "5m"         # 5-minute candles
PERIOD       = "5d"         # Last 5 days of data

# Auto-refresh
REFRESH_SECONDS = 60        # Refresh every 60 seconds

# App branding
APP_TITLE    = "OPUS 4.7 · OIL TERMINAL"
APP_SUBTITLE = "Crude Oil Prediction Terminal · WTI Futures"
VERSION      = "v5.0"

# ── Phase 2 · OSINT News Scanner ─────────────────────────
GEMINI_API_KEY   = ""   # ← Paste your Gemini API key here
NEWS_MAX_PER_FEED = 5   # Headlines per RSS source

RSS_FEEDS = [
    {"name": "OilPrice",    "url": "https://oilprice.com/rss/main"},
    {"name": "Yahoo·WTI",   "url": "https://finance.yahoo.com/rss/headline?s=CL%3DF"},
    {"name": "MarketWatch", "url": "https://feeds.marketwatch.com/marketwatch/realtimeheadlines/"},
]

# Theme colors
COLOR_UP        = "#00ff88"   # Bullish candle
COLOR_DOWN      = "#ff3c3c"   # Bearish candle
COLOR_BG        = "#0a0a0f"   # Background
COLOR_PANEL     = "#0f0f1a"   # Panel background
COLOR_ACCENT    = "#00aaff"   # Accent / labels
COLOR_TEXT      = "#cccccc"   # Default text
COLOR_GOLD      = "#ffd700"   # Highlights

# Model confidence (Phase 1 = static placeholders)
MODEL_SCORES = {
    "MIROFISH"  : 94,
    "OPUS 4.7"  : 88,
    "GRAPH"     : 92,
    "OSINT"     : 85,
    "SENTIMENT" : 80,
}

# Oil factor weights (Phase 1 = static placeholders)
OIL_FACTORS = {
    "OPEC+"     : 80,
    "USD/DXY"   : 65,
    "INVENTORY" : 84,
    "GEOPOL"    : 87,
    "CHINA PMI" : 60,
    "REFINERIES": 75,
}
