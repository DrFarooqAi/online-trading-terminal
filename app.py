# ─────────────────────────────────────────
#  OIL TERMINAL · app.py
# ─────────────────────────────────────────

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import sys, os

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

TF_MAP = {
    "1m":  ("1m",  "1d"),
    "5m":  ("5m",  "5d"),
    "15m": ("15m", "5d"),
    "1H":  ("1h",  "30d"),
    "4H":  ("4h",  "60d"),
    "1D":  ("1d",  "365d"),
}

st.set_page_config(
    page_title="ONLINE TRADING TERMINAL",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="collapsed"
)
st_autorefresh(interval=REFRESH_SECONDS * 1000, key="price_refresh")

# ── CSS — no animations, no glows, no shadows ────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&display=swap');

.stApp {{
    background-color:{COLOR_BG};
    color:{COLOR_TEXT};
    font-family:'IBM Plex Mono','Trebuchet MS',monospace;
}}
#MainMenu,footer,header {{ visibility:hidden }}
.block-container {{
    padding-top:0.3rem;
    padding-bottom:1rem;
    padding-left:52px !important;
    padding-right:52px !important;
    max-width:100% !important;
}}
[data-testid="column"] {{ padding:0 3px }}
::-webkit-scrollbar {{ width:3px; height:3px }}
::-webkit-scrollbar-track {{ background:{COLOR_BG} }}
::-webkit-scrollbar-thumb {{ background:#2a2e39; border-radius:2px }}

/* ── Number inputs ── */
.stNumberInput input {{
    background-color:{COLOR_BG} !important;
    color:{COLOR_TEXT} !important;
    border:1px solid #2a2e39 !important;
    border-radius:3px !important;
    font-family:'IBM Plex Mono',monospace !important;
    font-size:11px !important;
    padding:4px 8px !important;
}}
.stNumberInput input:focus {{
    border-color:{COLOR_ACCENT} !important;
    box-shadow:none !important;
}}
.stNumberInput label {{
    color:#9ca3af !important;
    font-family:'IBM Plex Mono',monospace !important;
    font-size:9px !important;
    letter-spacing:.5px !important;
    text-transform:uppercase !important;
}}
div[data-testid="stForm"] {{
    background:{COLOR_PANEL};
    border:1px solid #2a2e39;
    border-radius:4px;
    padding:10px;
    margin-top:8px;
}}

/* ── Buttons ── */
.stButton > button {{
    background:transparent !important;
    border:1px solid #2a2e39 !important;
    color:#9ca3af !important;
    font-family:'IBM Plex Mono',monospace !important;
    font-size:10px !important;
    letter-spacing:.5px !important;
    border-radius:3px !important;
}}
.stButton > button:hover {{
    border-color:{COLOR_ACCENT} !important;
    color:{COLOR_TEXT} !important;
    background:{COLOR_ACCENT}12 !important;
}}
button[kind="primary"] {{
    background:{COLOR_UP}20 !important;
    border-color:{COLOR_UP} !important;
    color:{COLOR_UP} !important;
}}
button[kind="primary"]:hover {{ background:{COLOR_UP}35 !important }}
[data-testid="stPlotlyChart"] {{
    border:1px solid #2a2e39;
    border-radius:4px;
    overflow:hidden;
}}

/* ── Timeframe pills ── */
[data-testid="stPills"] {{ margin-bottom:0 !important }}
[data-testid="stPills"] button {{
    background:{COLOR_PANEL} !important;
    border:1px solid #2a2e39 !important;
    color:#9ca3af !important;
    font-family:'IBM Plex Mono',monospace !important;
    font-size:9px !important;
    border-radius:2px !important;
    padding:2px 9px !important;
    letter-spacing:.5px !important;
    min-height:unset !important;
    height:22px !important;
}}
[data-testid="stPills"] button:hover {{
    color:{COLOR_TEXT} !important;
    border-color:{COLOR_ACCENT} !important;
}}
[data-testid="stPills"] button[aria-checked="true"] {{
    background:{COLOR_ACCENT}25 !important;
    border-color:{COLOR_ACCENT} !important;
    color:#fff !important;
}}
[data-testid="stPills"] [data-testid="stWidgetLabel"] {{ display:none !important }}

/* ── Fixed toolbar buttons ── */
.tv-tb-btn {{
    width:32px; height:30px;
    display:flex; align-items:center; justify-content:center;
    color:#4a5568; font-size:14px; cursor:default; border-radius:3px;
}}
.tv-tb-btn.on {{ background:{COLOR_ACCENT}22; color:{COLOR_ACCENT} }}
.tv-tb-sep {{ width:20px; height:1px; background:#2a2e39; margin:3px auto }}

/* ── Tablet ≤1100px ── */
@media(max-width:1100px) {{
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child {{ display:none !important }}
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) {{ flex:1 1 65% !important; max-width:65% !important }}
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child   {{ flex:1 1 35% !important; max-width:35% !important }}
    .block-container {{ padding-left:46px !important; padding-right:46px !important }}
}}
/* ── Mobile ≤768px ── */
@media(max-width:768px) {{
    [data-testid="stHorizontalBlock"] {{ flex-direction:column !important }}
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{
        width:100% !important; min-width:100% !important; max-width:100% !important; display:block !important;
    }}
    .block-container {{ padding-left:8px !important; padding-right:8px !important }}
    .tv-fixed-toolbar {{ display:none !important }}
}}
</style>
""", unsafe_allow_html=True)

# ── Fixed side toolbars (no border overlay — removed) ─────
st.html(f"""
<div class='tv-fixed-toolbar' style='
    position:fixed; left:4px; top:50%; transform:translateY(-50%);
    background:{COLOR_PANEL}; border:1px solid #2a2e39; border-radius:4px;
    padding:5px 3px; z-index:200;
    display:flex; flex-direction:column; align-items:center; gap:0;'>
  <div class='tv-tb-btn on'>⊕</div>
  <div class='tv-tb-sep'></div>
  <div class='tv-tb-btn'>╱</div>
  <div class='tv-tb-btn'>━</div>
  <div class='tv-tb-btn'>┃</div>
  <div class='tv-tb-btn'>↗</div>
  <div class='tv-tb-sep'></div>
  <div class='tv-tb-btn'>▭</div>
  <div class='tv-tb-btn'>◯</div>
  <div class='tv-tb-sep'></div>
  <div class='tv-tb-btn'>ƒ</div>
  <div class='tv-tb-btn'>⑂</div>
  <div class='tv-tb-sep'></div>
  <div class='tv-tb-btn'>T</div>
  <div class='tv-tb-btn'>⟷</div>
  <div class='tv-tb-sep'></div>
  <div class='tv-tb-btn'>🔒</div>
  <div class='tv-tb-btn' style='color:#f2364560;'>⊗</div>
</div>

<div class='tv-fixed-toolbar' style='
    position:fixed; right:4px; top:50%; transform:translateY(-50%);
    background:{COLOR_PANEL}; border:1px solid #2a2e39; border-radius:4px;
    padding:5px 3px; z-index:200;
    display:flex; flex-direction:column; align-items:center; gap:0;'>
  <div class='tv-tb-btn on' style='color:{COLOR_ACCENT};'>≡</div>
  <div class='tv-tb-sep'></div>
  <div class='tv-tb-btn'>◫</div>
  <div class='tv-tb-btn'>∿</div>
  <div class='tv-tb-btn'>◉</div>
  <div class='tv-tb-sep'></div>
  <div class='tv-tb-btn on' style='color:{COLOR_UP};'>◈</div>
  <div class='tv-tb-btn'>⊞</div>
  <div class='tv-tb-sep'></div>
  <div class='tv-tb-btn'>▤</div>
  <div class='tv-tb-sep'></div>
  <div class='tv-tb-btn'>⚙</div>
</div>
""")

# ── Data ─────────────────────────────────────────────────
wti_price   = get_current_price(TICKER_WTI)
brent_price = get_current_price(TICKER_BRENT)
wti_df_base = get_ohlcv(TICKER_WTI)
vol_summary = get_volume_summary(wti_df_base)

raw_news   = get_news_headlines()
titles     = tuple(item["title"] for item in raw_news)
tag_map    = tag_headlines(titles)
news_items = [{**item, "tag": tag_map.get(item["title"], "NEUTRAL")} for item in raw_news]

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

auto_close_on_price(wti_price["price"])
maybe_log_signal(signal, wti_price["price"])
pnl_stats     = get_stats()
recent_trades = get_recent_trades(20)
open_trades   = get_open_trades()

# ── Derived display values ────────────────────────────────
wti_c    = COLOR_UP   if wti_price["change"] >= 0 else COLOR_DOWN
brent_c  = COLOR_UP   if brent_price["change"] >= 0 else COLOR_DOWN
wti_a    = "▲" if wti_price["change"] >= 0 else "▼"
brent_a  = "▲" if brent_price["change"] >= 0 else "▼"
sig_dir  = signal.get("direction", "—") if signal else "—"
sig_conf = signal.get("confidence", 0)  if signal else 0
sig_col  = COLOR_UP if sig_dir == "LONG" else COLOR_DOWN if sig_dir == "SHORT" else "#9ca3af"
sig_icon = "▲" if sig_dir == "LONG" else "▼" if sig_dir == "SHORT" else "◆"
conv_col = COLOR_UP if conv["direction"] == "BULLISH" else COLOR_DOWN if conv["direction"] == "BEARISH" else COLOR_GOLD

# ── Header bar ───────────────────────────────────────────
st.html(f"""
<div style='
    background:{COLOR_PANEL};
    border-bottom:2px solid {COLOR_ACCENT}55;
    padding:8px 14px;
    display:flex; align-items:center; justify-content:space-between; gap:10px;
'>
  <!-- Logo -->
  <div style='display:flex;align-items:center;gap:10px;flex-shrink:0;'>
    <div style='
        width:32px; height:32px; border-radius:6px;
        background:{COLOR_ACCENT};
        display:flex; align-items:center; justify-content:center; font-size:16px;
    '>🛢</div>
    <div>
      <div style='color:#fff;font-family:"IBM Plex Mono",monospace;font-size:12px;font-weight:600;letter-spacing:.5px;'>{APP_TITLE}</div>
      <div style='color:#6b7280;font-family:"IBM Plex Mono",monospace;font-size:8px;margin-top:1px;'>{APP_SUBTITLE} · {VERSION}</div>
    </div>
  </div>

  <!-- Price tiles -->
  <div style='display:flex;flex:1;justify-content:center;flex-wrap:wrap;'>
    <div style='padding:4px 16px;border-right:1px solid #2a2e39;text-align:center;'>
      <div style='color:#9ca3af;font-family:"IBM Plex Mono",monospace;font-size:8px;letter-spacing:1px;margin-bottom:2px;'>WTI CRUDE</div>
      <div style='color:{wti_c};font-family:"IBM Plex Mono",monospace;font-size:18px;font-weight:600;line-height:1;'>${wti_price["price"]:.2f}</div>
      <div style='color:{wti_c};font-family:"IBM Plex Mono",monospace;font-size:10px;margin-top:2px;'>{wti_a} {wti_price["change"]:+.2f} ({wti_price["change_p"]:+.2f}%)</div>
    </div>
    <div style='padding:4px 16px;border-right:1px solid #2a2e39;text-align:center;'>
      <div style='color:#9ca3af;font-family:"IBM Plex Mono",monospace;font-size:8px;letter-spacing:1px;margin-bottom:2px;'>BRENT</div>
      <div style='color:{brent_c};font-family:"IBM Plex Mono",monospace;font-size:18px;font-weight:600;line-height:1;'>${brent_price["price"]:.2f}</div>
      <div style='color:{brent_c};font-family:"IBM Plex Mono",monospace;font-size:10px;margin-top:2px;'>{brent_a} {brent_price["change"]:+.2f} ({brent_price["change_p"]:+.2f}%)</div>
    </div>
    <div style='padding:4px 16px;border-right:1px solid #2a2e39;text-align:center;'>
      <div style='color:#9ca3af;font-family:"IBM Plex Mono",monospace;font-size:8px;letter-spacing:1px;margin-bottom:2px;'>VOLUME</div>
      <div style='color:{COLOR_TEXT};font-family:"IBM Plex Mono",monospace;font-size:15px;font-weight:500;line-height:1;'>{vol_summary["current"]:,}</div>
      <div style='color:#6b7280;font-family:"IBM Plex Mono",monospace;font-size:9px;margin-top:2px;'>AVG {vol_summary["avg"]:,}</div>
    </div>
    <div style='padding:4px 16px;border-right:1px solid #2a2e39;text-align:center;'>
      <div style='color:#9ca3af;font-family:"IBM Plex Mono",monospace;font-size:8px;letter-spacing:1px;margin-bottom:2px;'>AI SIGNAL</div>
      <div style='color:{sig_col};font-family:"IBM Plex Mono",monospace;font-size:16px;font-weight:600;line-height:1;'>{sig_icon} {sig_dir}</div>
      <div style='color:{sig_col};font-family:"IBM Plex Mono",monospace;font-size:9px;margin-top:2px;'>{sig_conf}% CONF</div>
    </div>
    <div style='padding:4px 16px;text-align:center;'>
      <div style='color:#9ca3af;font-family:"IBM Plex Mono",monospace;font-size:8px;letter-spacing:1px;margin-bottom:2px;'>MIROFISH</div>
      <div style='color:{conv_col};font-family:"IBM Plex Mono",monospace;font-size:13px;font-weight:600;line-height:1;'>{conv["direction"]}</div>
      <div style='color:#6b7280;font-family:"IBM Plex Mono",monospace;font-size:9px;margin-top:2px;'>SCORE {conv["score"]:+}</div>
    </div>
  </div>

  <!-- Status -->
  <div style='flex-shrink:0;text-align:right;'>
    <div style='display:flex;align-items:center;gap:6px;justify-content:flex-end;'>
      <div style='width:7px;height:7px;border-radius:50%;background:{COLOR_UP};'></div>
      <span style='color:{COLOR_UP};font-family:"IBM Plex Mono",monospace;font-size:10px;font-weight:600;letter-spacing:2px;'>LIVE</span>
    </div>
    <div style='color:#6b7280;font-family:"IBM Plex Mono",monospace;font-size:8px;margin-top:3px;'>↻ {REFRESH_SECONDS}s</div>
  </div>
</div>
""")

# ── Timeframe selector ────────────────────────────────────
tf_col, _ = st.columns([2, 8])
with tf_col:
    selected_tf = st.pills("TF", options=list(TF_MAP.keys()), default="5m", key="chart_tf")

yf_interval, yf_period = TF_MAP.get(selected_tf or "5m", ("5m", "5d"))
wti_df = get_ohlcv(TICKER_WTI, interval=yf_interval, period=yf_period)

# ── 3-column chart layout ─────────────────────────────────
left_col, chart_col, right_col = st.columns([1.4, 5, 1.85])

with left_col:
    render_left_panel(wti_price, brent_price)

with chart_col:
    if not wti_df.empty:
        if isinstance(wti_df.columns, pd.MultiIndex):
            wti_df.columns = wti_df.columns.get_level_values(0)
        high  = float(wti_df["High"].max())
        low   = float(wti_df["Low"].min())
        close = float(wti_df["Close"].iloc[-1])
        open_ = float(wti_df["Open"].iloc[-1])
    else:
        high = low = close = open_ = 0.0

    st.html(f"""
    <div style='
        font-family:"IBM Plex Mono",monospace; font-size:10px; color:#6b7280;
        padding:3px 0 5px 2px;
        display:flex; gap:14px; align-items:center;
        border-bottom:1px solid #2a2e39; margin-bottom:4px; flex-wrap:wrap;
    '>
      <span style='color:#fff;font-weight:600;font-size:12px;'>CL=F</span>
      <span style='font-size:9px;'>WTI CRUDE · {selected_tf or "5m"}</span>
      <span style='color:#2a2e39;'>|</span>
      <span>O <span style='color:{COLOR_TEXT};'>${open_:.2f}</span></span>
      <span>H <span style='color:{COLOR_UP};'>${high:.2f}</span></span>
      <span>L <span style='color:{COLOR_DOWN};'>${low:.2f}</span></span>
      <span>C <span style='color:{COLOR_TEXT};'>${close:.2f}</span></span>
      <span style='color:#2a2e39;'>|</span>
      <span>VOL <span style='color:{COLOR_TEXT};'>{vol_summary["current"]:,}</span></span>
    </div>
    """)

    fig = build_candlestick_chart(wti_df, f"CL=F · WTI CRUDE · {selected_tf or '5m'}")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with right_col:
    render_right_panel(news_items, signal)
    render_trade_form(wti_price["price"], signal, open_trades)

# ── MIROFISH ─────────────────────────────────────────────
st.html(f"""
<div style='display:flex;align-items:center;gap:8px;padding:10px 2px 6px;border-top:1px solid #2a2e39;margin-top:6px;'>
  <div style='width:3px;height:14px;background:{COLOR_ACCENT};border-radius:2px;'></div>
  <span style='color:#e2e8f0;font-family:"IBM Plex Mono",monospace;font-size:11px;font-weight:600;letter-spacing:1px;'>MIROFISH</span>
  <span style='color:#6b7280;font-family:"IBM Plex Mono",monospace;font-size:9px;'>RELATIONSHIP GRAPH · PHASE 3</span>
  <div style='flex:1;height:1px;background:#2a2e39;margin-left:4px;'></div>
</div>
""")
render_graph_panel()

# ── PNL TRACKER ──────────────────────────────────────────
st.html(f"""
<div style='display:flex;align-items:center;gap:8px;padding:10px 2px 6px;border-top:1px solid #2a2e39;margin-top:4px;'>
  <div style='width:3px;height:14px;background:{COLOR_GOLD};border-radius:2px;'></div>
  <span style='color:#e2e8f0;font-family:"IBM Plex Mono",monospace;font-size:11px;font-weight:600;letter-spacing:1px;'>PNL TRACKER</span>
  <span style='color:#6b7280;font-family:"IBM Plex Mono",monospace;font-size:9px;'>EQUITY CURVE · TRADE LOG</span>
  <div style='flex:1;height:1px;background:#2a2e39;margin-left:4px;'></div>
</div>
""")
render_pnl_panel(pnl_stats, recent_trades)
render_pnl_bar(pnl_stats)

# ── Footer ────────────────────────────────────────────────
st.html(f"""
<div style='
    display:flex; align-items:center; justify-content:center; gap:12px;
    border-top:1px solid #2a2e39; padding:6px 16px; margin-top:4px;
    color:#6b7280; font-family:"IBM Plex Mono",monospace; font-size:8px; letter-spacing:.4px; flex-wrap:wrap;
'>
  <span style='color:#9ca3af;font-weight:500;'>{APP_TITLE}</span>
  <span>·</span><span>{VERSION}</span>
  <span>·</span><span>Yahoo Finance · 15-min delay</span>
  <span>·</span><span style='color:{COLOR_UP};'>Phases 1–5 Active</span>
  <span>·</span><span>yfinance · Streamlit · Plotly · D3.js · SQLite</span>
</div>
""")
