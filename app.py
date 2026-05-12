# ─────────────────────────────────────────
#  OIL TERMINAL · app.py
#  Main entry point — run with: streamlit run app.py
# ─────────────────────────────────────────

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from config import (
    APP_TITLE, APP_SUBTITLE, VERSION,
    TICKER_WTI, TICKER_BRENT,
    COLOR_BG, COLOR_PANEL, COLOR_ACCENT, COLOR_UP, COLOR_DOWN, COLOR_GOLD, COLOR_TEXT,
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

init_db()

st.set_page_config(
    page_title="ONLINE TRADING TERMINAL",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st_autorefresh(interval=REFRESH_SECONDS * 1000, key="price_refresh")

# ── Global CSS ────────────────────────────────────────────
st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&display=swap');

        .stApp {{
            background-color: {COLOR_BG};
            color: {COLOR_TEXT};
            font-family: 'IBM Plex Mono', 'Trebuchet MS', monospace;
        }}
        #MainMenu, footer, header {{ visibility: hidden; }}
        .block-container {{
            padding-top: 0.4rem;
            padding-bottom: 0rem;
            padding-left: 0.75rem;
            padding-right: 0.75rem;
            max-width: 100% !important;
        }}
        [data-testid="column"] {{ padding: 0 3px; }}

        /* ── Neon gradient border (TradingView premium feel) ── */
        .stApp::after {{
            content: '';
            position: fixed;
            inset: 0;
            border: 2px solid transparent;
            background:
                linear-gradient({COLOR_BG}, {COLOR_BG}) padding-box,
                linear-gradient(135deg, {COLOR_ACCENT}cc, #9c27b0cc, {COLOR_ACCENT}88, #9c27b0cc) border-box;
            pointer-events: none;
            z-index: 9998;
            animation: borderPulse 4s ease-in-out infinite;
        }}
        @keyframes borderPulse {{
            0%, 100% {{ opacity: 0.55; }}
            50%       {{ opacity: 1;    }}
        }}
        @keyframes livePulse {{
            0%, 100% {{ opacity: 1;   box-shadow: 0 0 5px {COLOR_UP}; }}
            50%       {{ opacity: 0.4; box-shadow: 0 0 14px {COLOR_UP}; }}
        }}

        /* ── Scrollbar ── */
        ::-webkit-scrollbar {{ width: 3px; height: 3px; }}
        ::-webkit-scrollbar-track {{ background: {COLOR_BG}; }}
        ::-webkit-scrollbar-thumb {{ background: #2a2e39; border-radius: 2px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #363a45; }}

        /* ── Number inputs ── */
        .stNumberInput input {{
            background-color: {COLOR_BG} !important;
            color: {COLOR_TEXT} !important;
            border: 1px solid #2a2e39 !important;
            border-radius: 3px !important;
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 11px !important;
            padding: 4px 8px !important;
        }}
        .stNumberInput input:focus {{
            border-color: {COLOR_ACCENT} !important;
            box-shadow: 0 0 0 1px {COLOR_ACCENT}40 !important;
        }}
        .stNumberInput label {{
            color: #787b86 !important;
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 9px !important;
            letter-spacing: 0.5px !important;
            text-transform: uppercase !important;
        }}

        /* ── Form container ── */
        div[data-testid="stForm"] {{
            background: {COLOR_PANEL};
            border: 1px solid #2a2e39;
            border-radius: 4px;
            padding: 10px;
            margin-top: 8px;
        }}

        /* ── Buttons ── */
        .stButton > button {{
            background: transparent !important;
            border: 1px solid #2a2e39 !important;
            color: #787b86 !important;
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 10px !important;
            letter-spacing: 0.5px !important;
            border-radius: 3px !important;
            transition: all 0.15s ease !important;
        }}
        .stButton > button:hover {{
            border-color: {COLOR_ACCENT} !important;
            color: {COLOR_TEXT} !important;
        }}
        button[kind="primary"] {{
            background: {COLOR_UP}18 !important;
            border-color: {COLOR_UP}60 !important;
            color: {COLOR_UP} !important;
        }}
        button[kind="primary"]:hover {{
            background: {COLOR_UP}30 !important;
        }}

        /* ── Plotly chart ── */
        [data-testid="stPlotlyChart"] {{
            border: 1px solid #2a2e39;
            border-radius: 4px;
            overflow: hidden;
        }}

        /* ── TradingView-style tab bar ── */
        [data-testid="stTabs"] {{
            background: {COLOR_BG};
        }}
        [data-testid="stTabsList"] {{
            background: {COLOR_PANEL} !important;
            border-bottom: 1px solid #2a2e39 !important;
            border-radius: 0 !important;
            gap: 0 !important;
            padding: 0 6px !important;
            margin-bottom: 6px !important;
        }}
        [data-testid="stTabsList"] button {{
            background: transparent !important;
            border: none !important;
            border-bottom: 2px solid transparent !important;
            border-radius: 0 !important;
            color: #787b86 !important;
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 10px !important;
            letter-spacing: 0.8px !important;
            padding: 8px 16px !important;
            margin-bottom: -1px !important;
            transition: all 0.15s ease !important;
        }}
        [data-testid="stTabsList"] button:hover {{
            color: {COLOR_TEXT} !important;
            background: {COLOR_ACCENT}08 !important;
        }}
        [data-testid="stTabsList"] button[aria-selected="true"] {{
            color: {COLOR_TEXT} !important;
            border-bottom: 2px solid {COLOR_ACCENT} !important;
            background: {COLOR_ACCENT}0a !important;
        }}
        [data-testid="stTabPanel"] {{
            padding-top: 4px !important;
        }}

        /* ── Tablet responsive (iPad 768–1100px) ── */
        @media (max-width: 1100px) {{
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child {{
                display: none !important;
            }}
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) {{
                flex: 1 1 64% !important;
                max-width: 64% !important;
            }}
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child {{
                flex: 1 1 36% !important;
                max-width: 36% !important;
            }}
        }}

        /* ── Mobile (< 768px) ── */
        @media (max-width: 768px) {{
            [data-testid="stHorizontalBlock"] {{
                flex-direction: column !important;
            }}
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{
                width: 100% !important;
                min-width: 100% !important;
                max-width: 100% !important;
                display: block !important;
            }}
            .block-container {{
                padding-left: 0.3rem !important;
                padding-right: 0.3rem !important;
            }}
            [data-testid="stTabsList"] button {{
                font-size: 9px !important;
                padding: 7px 10px !important;
                letter-spacing: 0.3px !important;
            }}
        }}
    </style>
""", unsafe_allow_html=True)

# ── Fetch Data ────────────────────────────────────────────
wti_price   = get_current_price(TICKER_WTI)
brent_price = get_current_price(TICKER_BRENT)
wti_df      = get_ohlcv(TICKER_WTI)
vol_summary = get_volume_summary(wti_df)

# ── Fetch & Tag News ──────────────────────────────────────
raw_news   = get_news_headlines()
titles     = tuple(item["title"] for item in raw_news)
tag_map    = tag_headlines(titles)
news_items = [{**item, "tag": tag_map.get(item["title"], "NEUTRAL")} for item in raw_news]

# ── Graph Convergence + AI Signal ─────────────────────────
graph_data = get_graph_data()
conv       = get_convergence_score(graph_data["links"])
news_bull  = sum(1 for n in news_items if n["tag"] == "BULL")
news_bear  = sum(1 for n in news_items if n["tag"] == "BEAR")
top_hl     = tuple((n["tag"], n["title"][:100]) for n in news_items[:5])
signal     = get_trade_signal(
    wti_price         = wti_price["price"],
    wti_change        = wti_price["change"],
    brent_price       = brent_price["price"],
    convergence_score = conv["score"],
    convergence_dir   = conv["direction"],
    bull_strength     = conv["bull_str"],
    bear_strength     = conv["bear_str"],
    news_bull         = news_bull,
    news_bear         = news_bear,
    top_headlines     = top_hl,
)

# ── PnL Tracker ───────────────────────────────────────────
auto_close_on_price(wti_price["price"])
maybe_log_signal(signal, wti_price["price"])
pnl_stats     = get_stats()
recent_trades = get_recent_trades(20)
open_trades   = get_open_trades()

# ── Header bar ───────────────────────────────────────────
wti_change_color   = COLOR_UP if wti_price["change"] >= 0 else COLOR_DOWN
brent_change_color = COLOR_UP if brent_price["change"] >= 0 else COLOR_DOWN
wti_arrow   = "▲" if wti_price["change"] >= 0 else "▼"
brent_arrow = "▲" if brent_price["change"] >= 0 else "▼"

signal_dir   = signal.get("direction", "—") if signal else "—"
signal_conf  = signal.get("confidence", 0)  if signal else 0
signal_color = COLOR_UP if signal_dir == "LONG" else COLOR_DOWN if signal_dir == "SHORT" else "#787b86"
signal_icon  = "▲" if signal_dir == "LONG" else "▼" if signal_dir == "SHORT" else "◆"

st.html(f"""
    <div style='
        background:{COLOR_PANEL};
        border-bottom:1px solid #2a2e39;
        padding:7px 14px;
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap:12px;
    '>
        <!-- Branding -->
        <div style='display:flex;align-items:center;gap:10px;flex-shrink:0;'>
            <div style='
                width:30px;height:30px;border-radius:5px;
                background:linear-gradient(135deg,{COLOR_ACCENT},{COLOR_ACCENT}88);
                display:flex;align-items:center;justify-content:center;
                font-size:15px;
                box-shadow:0 0 12px {COLOR_ACCENT}55;
            '>🛢</div>
            <div>
                <div style='color:{COLOR_TEXT};font-family:"IBM Plex Mono",monospace;font-size:12px;font-weight:600;letter-spacing:0.5px;'>
                    {APP_TITLE}
                </div>
                <div style='color:#787b86;font-family:"IBM Plex Mono",monospace;font-size:8px;margin-top:1px;letter-spacing:0.3px;'>
                    {APP_SUBTITLE} &nbsp;·&nbsp; {VERSION}
                </div>
            </div>
        </div>

        <!-- Price tickers -->
        <div style='display:flex;gap:0;flex:1;justify-content:center;'>
            <div style='padding:4px 18px;border-right:1px solid #2a2e39;text-align:center;'>
                <div style='color:#787b86;font-family:"IBM Plex Mono",monospace;font-size:8px;letter-spacing:1px;margin-bottom:2px;'>WTI CRUDE</div>
                <div style='color:{COLOR_TEXT};font-family:"IBM Plex Mono",monospace;font-size:17px;font-weight:600;line-height:1;'>${wti_price["price"]:.2f}</div>
                <div style='color:{wti_change_color};font-family:"IBM Plex Mono",monospace;font-size:10px;margin-top:2px;'>
                    {wti_arrow} {wti_price["change"]:+.2f}
                    <span style='opacity:0.65;'>({wti_price["change_p"]:+.2f}%)</span>
                </div>
            </div>
            <div style='padding:4px 18px;border-right:1px solid #2a2e39;text-align:center;'>
                <div style='color:#787b86;font-family:"IBM Plex Mono",monospace;font-size:8px;letter-spacing:1px;margin-bottom:2px;'>BRENT</div>
                <div style='color:{COLOR_TEXT};font-family:"IBM Plex Mono",monospace;font-size:17px;font-weight:600;line-height:1;'>${brent_price["price"]:.2f}</div>
                <div style='color:{brent_change_color};font-family:"IBM Plex Mono",monospace;font-size:10px;margin-top:2px;'>
                    {brent_arrow} {brent_price["change"]:+.2f}
                    <span style='opacity:0.65;'>({brent_price["change_p"]:+.2f}%)</span>
                </div>
            </div>
            <div style='padding:4px 18px;border-right:1px solid #2a2e39;text-align:center;'>
                <div style='color:#787b86;font-family:"IBM Plex Mono",monospace;font-size:8px;letter-spacing:1px;margin-bottom:2px;'>VOLUME</div>
                <div style='color:{COLOR_TEXT};font-family:"IBM Plex Mono",monospace;font-size:15px;font-weight:500;line-height:1;'>{vol_summary["current"]:,}</div>
                <div style='color:#4a4e5a;font-family:"IBM Plex Mono",monospace;font-size:9px;margin-top:2px;'>AVG {vol_summary["avg"]:,}</div>
            </div>
            <div style='padding:4px 18px;border-right:1px solid #2a2e39;text-align:center;'>
                <div style='color:#787b86;font-family:"IBM Plex Mono",monospace;font-size:8px;letter-spacing:1px;margin-bottom:2px;'>AI SIGNAL</div>
                <div style='color:{signal_color};font-family:"IBM Plex Mono",monospace;font-size:15px;font-weight:600;line-height:1;'>{signal_icon} {signal_dir}</div>
                <div style='color:{signal_color};opacity:0.7;font-family:"IBM Plex Mono",monospace;font-size:9px;margin-top:2px;'>{signal_conf}% CONF</div>
            </div>
            <div style='padding:4px 18px;text-align:center;'>
                <div style='color:#787b86;font-family:"IBM Plex Mono",monospace;font-size:8px;letter-spacing:1px;margin-bottom:2px;'>MIROFISH</div>
                <div style='
                    color:{"#089981" if conv["direction"]=="BULLISH" else "#f23645" if conv["direction"]=="BEARISH" else COLOR_GOLD};
                    font-family:"IBM Plex Mono",monospace;font-size:13px;font-weight:600;line-height:1;
                '>{conv["direction"]}</div>
                <div style='color:#4a4e5a;font-family:"IBM Plex Mono",monospace;font-size:9px;margin-top:2px;'>SCORE {conv["score"]:+}</div>
            </div>
        </div>

        <!-- Live indicator -->
        <div style='display:flex;align-items:center;gap:16px;flex-shrink:0;'>
            <div style='text-align:right;'>
                <div style='display:flex;align-items:center;gap:5px;justify-content:flex-end;'>
                    <div style='
                        width:7px;height:7px;border-radius:50%;
                        background:{COLOR_UP};
                        box-shadow:0 0 8px {COLOR_UP};
                        animation:livePulse 2s ease-in-out infinite;
                    '></div>
                    <span style='color:{COLOR_UP};font-family:"IBM Plex Mono",monospace;font-size:10px;font-weight:600;letter-spacing:1.5px;'>LIVE</span>
                </div>
                <div style='color:#4a4e5a;font-family:"IBM Plex Mono",monospace;font-size:8px;margin-top:3px;text-align:right;'>↻ {REFRESH_SECONDS}s</div>
            </div>
        </div>
    </div>
""")

# ── MAIN TABS (TradingView-style) ─────────────────────────
tab_chart, tab_mirofish, tab_pnl = st.tabs([
    "📊  CHART  ·  CL=F",
    "🌐  MIROFISH  ·  GRAPH",
    "📈  PNL  ·  EQUITY",
])

# ── TAB 1 · CHART ─────────────────────────────────────────
with tab_chart:
    left_col, chart_col, right_col = st.columns([1.5, 5, 1.8])

    with left_col:
        render_left_panel(wti_price, brent_price)

    with chart_col:
        if not wti_df.empty:
            if isinstance(wti_df.columns, __import__('pandas').MultiIndex):
                wti_df.columns = wti_df.columns.get_level_values(0)
            high  = float(wti_df["High"].max())
            low   = float(wti_df["Low"].min())
            close = float(wti_df["Close"].iloc[-1])
            open_ = float(wti_df["Open"].iloc[-1])
        else:
            high = low = close = open_ = 0.0

        st.html(f"""
            <div style='
                font-family:"IBM Plex Mono",monospace;font-size:10px;color:#787b86;
                padding:4px 0 5px 2px;
                display:flex;gap:16px;align-items:center;
                border-bottom:1px solid #2a2e39;margin-bottom:4px;flex-wrap:wrap;
            '>
                <span style='color:{COLOR_TEXT};font-weight:600;font-size:11px;'>CL=F</span>
                <span style='color:#787b86;font-size:9px;'>WTI CRUDE · 5M</span>
                <span style='color:#4a4e5a;'>|</span>
                <span>O <span style='color:{COLOR_TEXT}'>${open_:.2f}</span></span>
                <span>H <span style='color:{COLOR_UP}'>${high:.2f}</span></span>
                <span>L <span style='color:{COLOR_DOWN}'>${low:.2f}</span></span>
                <span>C <span style='color:{COLOR_TEXT}'>${close:.2f}</span></span>
                <span style='color:#4a4e5a;'>|</span>
                <span>VOL <span style='color:{COLOR_TEXT}'>{vol_summary["current"]:,}</span></span>
            </div>
        """)

        fig = build_candlestick_chart(wti_df, "CL=F · WTI CRUDE · 5M")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with right_col:
        render_right_panel(news_items, signal)
        render_trade_form(wti_price["price"], signal, open_trades)

# ── TAB 2 · MIROFISH ──────────────────────────────────────
with tab_mirofish:
    st.html(f"""
        <div style='
            display:flex;align-items:center;gap:8px;
            padding:6px 4px 8px 4px;
        '>
            <div style='width:3px;height:14px;background:{COLOR_ACCENT};border-radius:2px;'></div>
            <span style='color:{COLOR_TEXT};font-family:"IBM Plex Mono",monospace;font-size:10px;font-weight:600;letter-spacing:1px;'>MIROFISH</span>
            <span style='color:#4a4e5a;font-family:"IBM Plex Mono",monospace;font-size:9px;'>RELATIONSHIP GRAPH · PHASE 3</span>
            <div style='flex:1;height:1px;background:#2a2e39;margin-left:4px;'></div>
        </div>
    """)
    render_graph_panel()

# ── TAB 3 · PNL TRACKER ───────────────────────────────────
with tab_pnl:
    render_pnl_panel(pnl_stats, recent_trades)

# ── BOTTOM PnL BAR (always visible) ───────────────────────
render_pnl_bar(pnl_stats)

# ── FOOTER ────────────────────────────────────────────────
st.html(f"""
    <div style='
        display:flex;align-items:center;justify-content:center;gap:14px;
        border-top:1px solid #2a2e39;
        padding:6px 16px;margin-top:4px;
        color:#4a4e5a;
        font-family:"IBM Plex Mono",monospace;
        font-size:8px;letter-spacing:0.5px;
        flex-wrap:wrap;
    '>
        <span style='color:#787b86;'>{APP_TITLE}</span>
        <span>·</span>
        <span>{VERSION}</span>
        <span>·</span>
        <span>Yahoo Finance</span>
        <span>·</span>
        <span>15-min delay</span>
        <span>·</span>
        <span style='color:{COLOR_UP};'>Phases 1–5 Active</span>
        <span>·</span>
        <span style='color:#4a4e5a;'>yfinance · Streamlit · Plotly · D3.js · SQLite</span>
    </div>
""")
