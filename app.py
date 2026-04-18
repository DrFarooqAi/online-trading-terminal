# ─────────────────────────────────────────
#  OIL TERMINAL · app.py
#  Main entry point — run with: streamlit run app.py
# ─────────────────────────────────────────

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import sys
import os

# Make sure local modules are importable
sys.path.insert(0, os.path.dirname(__file__))

from config import (
    APP_TITLE, APP_SUBTITLE, VERSION,
    TICKER_WTI, TICKER_BRENT,
    COLOR_BG, COLOR_ACCENT, COLOR_UP, COLOR_DOWN, COLOR_GOLD,
    REFRESH_SECONDS
)
from data.price_feed import get_ohlcv, get_current_price, get_volume_summary
from data.news_feed import get_news_headlines
from data.gemini_tagger import tag_headlines
from data.graph_data import get_graph_data, get_convergence_score
from data.signal_engine import get_trade_signal
from components.chart import build_candlestick_chart
from components.graph import render_graph_panel
from components.pnl_panel import render_pnl_panel
from components.panels import render_left_panel, render_right_panel, render_trade_form, render_pnl_bar
from data.trade_log import init_db, auto_close_on_price, maybe_log_signal, get_recent_trades, get_stats, get_open_trades

# ── DB init (idempotent) ─────────────────────────────────
init_db()

# ── Page config ──────────────────────────────────────────
st.set_page_config(
    page_title="ONLINE TRADING TERMINAL",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Auto-refresh every 60 seconds ───────────────────────
st_autorefresh(interval=REFRESH_SECONDS * 1000, key="price_refresh")

# ── Global CSS (st.markdown needed for page-level styles) ─
st.markdown(f"""
    <style>
        .stApp {{
            background-color: {COLOR_BG};
            color: #cccccc;
        }}
        #MainMenu, footer, header {{visibility: hidden;}}
        .block-container {{
            padding-top: 0.5rem;
            padding-bottom: 0rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }}
        [data-testid="column"] {{
            padding: 0 4px;
        }}
        ::-webkit-scrollbar {{ width: 4px; }}
        ::-webkit-scrollbar-track {{ background: #0a0a0f; }}
        ::-webkit-scrollbar-thumb {{ background: #1a1a3e; border-radius: 2px; }}
        .stNumberInput input {{
            background-color: #0f0f1a !important;
            color: #cccccc !important;
            border-color: #1a1a3e !important;
            font-family: monospace !important;
            font-size: 11px !important;
        }}
        .stNumberInput label {{
            color: #555 !important;
            font-family: monospace !important;
            font-size: 9px !important;
        }}
        div[data-testid="stForm"] {{
            background: #0f0f1a;
            border: 1px solid #1a1a3e;
            border-radius: 6px;
            padding: 10px;
            margin-top: 6px;
        }}
    </style>
""", unsafe_allow_html=True)

# ── Fetch Data ───────────────────────────────────────────
wti_price   = get_current_price(TICKER_WTI)
brent_price = get_current_price(TICKER_BRENT)
wti_df      = get_ohlcv(TICKER_WTI)
vol_summary = get_volume_summary(wti_df)

# ── Fetch & Tag News (Phase 2) ───────────────────────────
raw_news   = get_news_headlines()
titles     = tuple(item["title"] for item in raw_news)
tag_map    = tag_headlines(titles)
news_items = [{**item, "tag": tag_map.get(item["title"], "NEUTRAL")} for item in raw_news]

# ── Graph Convergence + AI Signal (Phase 3-4) ────────────
graph_data = get_graph_data()
conv       = get_convergence_score(graph_data["links"])
news_bull  = sum(1 for n in news_items if n["tag"] == "BULL")
news_bear  = sum(1 for n in news_items if n["tag"] == "BEAR")
top_hl     = tuple((n["tag"], n["title"][:100]) for n in news_items[:5])
signal     = get_trade_signal(
    wti_price        = wti_price["price"],
    wti_change       = wti_price["change"],
    brent_price      = brent_price["price"],
    convergence_score= conv["score"],
    convergence_dir  = conv["direction"],
    bull_strength    = conv["bull_str"],
    bear_strength    = conv["bear_str"],
    news_bull        = news_bull,
    news_bear        = news_bear,
    top_headlines    = top_hl,
)

# ── PnL Tracker (Phase 5) ────────────────────────────────
auto_close_on_price(wti_price["price"])
maybe_log_signal(signal, wti_price["price"])
pnl_stats     = get_stats()
recent_trades = get_recent_trades(20)
open_trades   = get_open_trades()

# ── TOP HEADER BAR ───────────────────────────────────────
wti_change_color   = COLOR_UP if wti_price["change"] >= 0 else COLOR_DOWN
brent_change_color = COLOR_UP if brent_price["change"] >= 0 else COLOR_DOWN
wti_arrow   = "▲" if wti_price["change"] >= 0 else "▼"
brent_arrow = "▲" if brent_price["change"] >= 0 else "▼"

st.html(f"""
    <div style='
        background:#0a0a14;
        border-bottom:1px solid #1a1a3e;
        padding:8px 16px;
        display:flex;
        align-items:center;
        justify-content:space-between;
        margin-bottom:8px;
    '>
        <!-- Left: Branding -->
        <div style='display:flex;align-items:center;gap:12px;'>
            <span style='font-size:20px;'>🛢️</span>
            <div>
                <div style='color:{COLOR_ACCENT};font-family:monospace;font-size:13px;font-weight:bold;'>
                    {APP_TITLE}
                </div>
                <div style='color:#444;font-family:monospace;font-size:9px;'>
                    {APP_SUBTITLE} · {VERSION}
                </div>
            </div>
        </div>

        <!-- Center: Prices -->
        <div style='display:flex;gap:40px;'>
            <div style='text-align:center;'>
                <div style='color:#555;font-family:monospace;font-size:9px;'>WTI CRUDE</div>
                <div style='color:#fff;font-family:monospace;font-size:16px;font-weight:bold;'>
                    ${wti_price["price"]:.2f}
                </div>
                <div style='color:{wti_change_color};font-family:monospace;font-size:10px;'>
                    {wti_arrow} {wti_price["change"]:+.2f} ({wti_price["change_p"]:+.2f}%)
                </div>
            </div>
            <div style='text-align:center;'>
                <div style='color:#555;font-family:monospace;font-size:9px;'>BRENT</div>
                <div style='color:#fff;font-family:monospace;font-size:16px;font-weight:bold;'>
                    ${brent_price["price"]:.2f}
                </div>
                <div style='color:{brent_change_color};font-family:monospace;font-size:10px;'>
                    {brent_arrow} {brent_price["change"]:+.2f} ({brent_price["change_p"]:+.2f}%)
                </div>
            </div>
            <div style='text-align:center;'>
                <div style='color:#555;font-family:monospace;font-size:9px;'>VOLUME</div>
                <div style='color:#ccc;font-family:monospace;font-size:14px;'>
                    {vol_summary["current"]:,}
                </div>
                <div style='color:#444;font-family:monospace;font-size:9px;'>
                    AVG {vol_summary["avg"]:,}
                </div>
            </div>
        </div>

        <!-- Right: Status -->
        <div style='text-align:right;'>
            <div style='display:flex;align-items:center;gap:6px;'>
                <div style='
                    width:8px;height:8px;border-radius:50%;
                    background:#00ff88;
                    box-shadow:0 0 6px #00ff88;
                '></div>
                <span style='color:#00ff88;font-family:monospace;font-size:11px;'>LIVE</span>
            </div>
            <div style='color:#444;font-family:monospace;font-size:9px;margin-top:4px;'>
                REFRESH · {REFRESH_SECONDS}s
            </div>
        </div>
    </div>
""")

# ── MAIN 3-COLUMN LAYOUT ─────────────────────────────────
left_col, chart_col, right_col = st.columns([1.5, 5, 1.8])

with left_col:
    render_left_panel(wti_price, brent_price)

with chart_col:
    # Chart subtitle bar
    if not wti_df.empty:
        if isinstance(wti_df.columns, __import__('pandas').MultiIndex):
            wti_df.columns = wti_df.columns.get_level_values(0)
        high  = float(wti_df["High"].max())
        low   = float(wti_df["Low"].min())
        close = float(wti_df["Close"].iloc[-1])
        oi_placeholder = "1.24M"
    else:
        high = low = close = 0.0
        oi_placeholder = "-"

    st.html(f"""
        <div style='
            font-family:monospace;font-size:10px;color:#666;
            padding:4px 0 6px 4px;
            display:flex;gap:20px;
        '>
            <span style='color:{COLOR_ACCENT};font-weight:bold;'>CL=F · WTI CRUDE · 5M</span>
            <span>VOL <span style='color:#ccc'>{vol_summary["current"]:,}</span></span>
            <span>HIGH <span style='color:{COLOR_UP}'>${high:.2f}</span></span>
            <span>LOW <span style='color:{COLOR_DOWN}'>${low:.2f}</span></span>
            <span>OI <span style='color:#ccc'>{oi_placeholder}</span></span>
        </div>
    """)

    fig = build_candlestick_chart(wti_df, "CL=F · WTI CRUDE · 5M")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with right_col:
    render_right_panel(news_items, signal)
    render_trade_form(wti_price["price"], signal, open_trades)

# ── PNL PANEL ────────────────────────────────────────────
render_pnl_panel(pnl_stats, recent_trades)

# ── MIROFISH GRAPH ───────────────────────────────────────
st.html("""
    <div style='
        color:#1a1a3e;font-family:monospace;font-size:9px;
        letter-spacing:2px;padding:4px 0 2px 2px;
    '>▸ MIROFISH · RELATIONSHIP GRAPH</div>
""")
render_graph_panel()

# ── BOTTOM PnL BAR ───────────────────────────────────────
render_pnl_bar(pnl_stats)

# ── FOOTER ───────────────────────────────────────────────
st.html(f"""
    <div style='
        text-align:center;
        color:#222;
        font-family:monospace;
        font-size:8px;
        margin-top:4px;
        padding-bottom:4px;
    '>
        {APP_TITLE} · {VERSION} · Data via Yahoo Finance · 15min delay ·
        Phases 1-4 Complete · Phase 5: PnL Tracker + SQLite coming next
    </div>
""")
