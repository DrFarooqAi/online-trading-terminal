# ─────────────────────────────────────────
#  OIL TERMINAL · components/panels.py
#  Left panel (model scores) + Right panel (news placeholder)
# ─────────────────────────────────────────

import streamlit as st
from config import MODEL_SCORES, OIL_FACTORS, COLOR_UP, COLOR_DOWN, COLOR_GOLD, COLOR_ACCENT, COLOR_PANEL, COLOR_TEXT

_TV = {
    "bg"      : "#131722",
    "panel"   : "#1e222d",
    "border"  : "#2a2e39",
    "text"    : "#d1d4dc",
    "muted"   : "#787b86",
    "dim"     : "#4a4e5a",
    "font"    : "'IBM Plex Mono', monospace",
}


def render_left_panel(wti_data: dict, brent_data: dict):
    """
    Renders the left sidebar panel:
    - Wallet / account info
    - Model confidence scores
    - Oil factor weights
    """

    st.html(f"""
        <div style='
            background:{_TV["panel"]};
            border:1px solid {_TV["border"]};
            border-radius:4px;
            padding:10px 12px;
            margin-bottom:8px;
        '>
            <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;'>
                <span style='color:{_TV["muted"]};font-size:9px;font-family:{_TV["font"]};letter-spacing:1px;'>ACCOUNT · BIN88888</span>
                <span style='
                    color:{COLOR_UP};font-size:8px;font-family:{_TV["font"]};
                    background:{COLOR_UP}15;border:1px solid {COLOR_UP}40;
                    padding:1px 6px;border-radius:2px;letter-spacing:1px;
                '>● ACTIVE</span>
            </div>
            <div style='color:{_TV["muted"]};font-size:8px;font-family:{_TV["font"]};letter-spacing:0.5px;margin-bottom:3px;'>30-DAY NET PROFIT</div>
            <div style='color:{COLOR_UP};font-size:20px;font-family:{_TV["font"]};font-weight:600;line-height:1;'>+$0.00</div>
            <div style='color:{_TV["dim"]};font-size:8px;font-family:{_TV["font"]};margin-top:3px;letter-spacing:0.5px;'>CRUDE OIL · SHORT/LONG</div>
            <div style='display:flex;gap:0;margin-top:10px;border-top:1px solid {_TV["border"]};padding-top:8px;'>
                <div style='flex:1;text-align:center;border-right:1px solid {_TV["border"]};'>
                    <div style='color:{_TV["muted"]};font-size:8px;font-family:{_TV["font"]};'>TRADES</div>
                    <div style='color:{_TV["text"]};font-size:14px;font-family:{_TV["font"]};font-weight:500;'>0</div>
                </div>
                <div style='flex:1;text-align:center;border-right:1px solid {_TV["border"]};'>
                    <div style='color:{_TV["muted"]};font-size:8px;font-family:{_TV["font"]};'>WIN %</div>
                    <div style='color:{_TV["text"]};font-size:14px;font-family:{_TV["font"]};font-weight:500;'>—</div>
                </div>
                <div style='flex:1;text-align:center;'>
                    <div style='color:{_TV["muted"]};font-size:8px;font-family:{_TV["font"]};'>R/R</div>
                    <div style='color:{_TV["text"]};font-size:14px;font-family:{_TV["font"]};font-weight:500;'>—</div>
                </div>
            </div>
        </div>
    """)

    # ── Model Confidence ─────────────────────────────────
    st.html(f"""
        <div style='display:flex;align-items:center;gap:6px;margin-bottom:8px;'>
            <div style='width:2px;height:11px;background:{COLOR_ACCENT};border-radius:1px;'></div>
            <span style='color:{_TV["muted"]};font-size:9px;font-family:{_TV["font"]};letter-spacing:1px;'>MODEL CONFIDENCE</span>
        </div>
    """)

    for model, score in MODEL_SCORES.items():
        color = COLOR_UP if score >= 90 else COLOR_GOLD if score >= 80 else "#e65c00"
        st.html(f"""
            <div style='margin-bottom:7px;'>
                <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:3px;'>
                    <span style='color:{_TV["text"]};font-size:9px;font-family:{_TV["font"]};'>{model}</span>
                    <span style='color:{color};font-size:9px;font-family:{_TV["font"]};font-weight:500;'>{score}%</span>
                </div>
                <div style='background:{_TV["bg"]};border-radius:1px;height:3px;'>
                    <div style='background:{color};width:{score}%;height:3px;border-radius:1px;opacity:0.85;'></div>
                </div>
            </div>
        """)

    st.html(f"<div style='border-top:1px solid {_TV['border']};margin:10px 0 8px;'></div>")

    # ── Oil Factor Weights ───────────────────────────────
    st.html(f"""
        <div style='display:flex;align-items:center;gap:6px;margin-bottom:8px;'>
            <div style='width:2px;height:11px;background:{COLOR_GOLD};border-radius:1px;'></div>
            <span style='color:{_TV["muted"]};font-size:9px;font-family:{_TV["font"]};letter-spacing:1px;'>OIL FACTOR WEIGHTS</span>
        </div>
    """)

    for factor, weight in OIL_FACTORS.items():
        color = COLOR_ACCENT if weight >= 80 else COLOR_GOLD if weight >= 65 else _TV["muted"]
        st.html(f"""
            <div style='margin-bottom:7px;'>
                <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:3px;'>
                    <span style='color:{_TV["text"]};font-size:9px;font-family:{_TV["font"]};'>{factor}</span>
                    <span style='color:{color};font-size:9px;font-family:{_TV["font"]};font-weight:500;'>{weight}%</span>
                </div>
                <div style='background:{_TV["bg"]};border-radius:1px;height:3px;'>
                    <div style='background:{color};width:{weight}%;height:3px;border-radius:1px;opacity:0.85;'></div>
                </div>
            </div>
        """)


def render_right_panel(news_items: list = None, signal: dict = None):
    if news_items is None:
        news_items = []

    tag_colors = {
        "BULL"   : (COLOR_UP,   f"{COLOR_UP}12",   f"{COLOR_UP}50"),
        "BEAR"   : (COLOR_DOWN, f"{COLOR_DOWN}12",  f"{COLOR_DOWN}50"),
        "NEUTRAL": (COLOR_GOLD, f"{COLOR_GOLD}12",  f"{COLOR_GOLD}50"),
    }

    gemini_active = bool(__import__("config").GEMINI_API_KEY)
    engine_label  = "GEMINI" if gemini_active else "KEYWORD"
    count_label   = f"{len(news_items)}" if news_items else "0"

    st.html(f"""
        <div style='
            background:{_TV["panel"]};
            border:1px solid {_TV["border"]};
            border-radius:4px 4px 0 0;
            padding:8px 10px 6px;
        '>
            <div style='display:flex;justify-content:space-between;align-items:center;'>
                <div style='display:flex;align-items:center;gap:6px;'>
                    <div style='width:2px;height:11px;background:{COLOR_ACCENT};border-radius:1px;'></div>
                    <span style='color:{_TV["text"]};font-size:10px;font-family:{_TV["font"]};font-weight:500;letter-spacing:0.5px;'>NEWS SCANNER</span>
                </div>
                <div style='display:flex;align-items:center;gap:6px;'>
                    <span style='color:{_TV["dim"]};font-size:8px;font-family:{_TV["font"]};'>{engine_label}</span>
                    <span style='
                        background:{COLOR_ACCENT}15;color:{COLOR_ACCENT};
                        font-size:8px;font-family:{_TV["font"]};
                        padding:1px 5px;border-radius:2px;border:1px solid {COLOR_ACCENT}30;
                    '>{count_label} HEADLINES</span>
                </div>
            </div>
            <div style='color:{_TV["dim"]};font-size:8px;font-family:{_TV["font"]};margin-top:3px;'>
                OilPrice · Yahoo Finance · MarketWatch · 5m cache
            </div>
        </div>
    """)

    if not news_items:
        st.html(f"""
            <div style='
                background:{_TV["panel"]};border:1px solid {_TV["border"]};border-top:none;
                border-radius:0 0 4px 4px;padding:20px;text-align:center;
            '>
                <span style='color:{_TV["muted"]};font-size:10px;font-family:{_TV["font"]};'>No headlines loaded</span>
            </div>
        """)
    else:
        rows_html = ""
        for item in news_items:
            tag   = item.get("tag", "NEUTRAL")
            color, bg, border = tag_colors.get(tag, tag_colors["NEUTRAL"])
            title = item["title"]
            short = title if len(title) <= 56 else title[:53] + "…"
            src   = item.get("source", "")
            rows_html += f"""
                <div style='
                    padding:6px 10px;
                    border-bottom:1px solid {_TV["bg"]};
                    transition:background 0.1s;
                '>
                    <div style='display:flex;align-items:flex-start;gap:6px;'>
                        <span style='
                            background:{bg};color:{color};border:1px solid {border};
                            font-family:{_TV["font"]};font-size:7px;font-weight:600;
                            padding:1px 5px;border-radius:2px;
                            white-space:nowrap;margin-top:2px;flex-shrink:0;letter-spacing:0.5px;
                        '>{tag}</span>
                        <span style='color:{_TV["text"]};font-family:{_TV["font"]};font-size:9px;line-height:1.45;'>
                            {short}
                        </span>
                    </div>
                    <div style='color:{_TV["dim"]};font-family:{_TV["font"]};font-size:8px;margin-top:2px;padding-left:38px;'>
                        {src}
                    </div>
                </div>
            """

        st.html(f"""
            <div style='
                background:{_TV["bg"]};border:1px solid {_TV["border"]};border-top:none;
                border-radius:0 0 4px 4px;max-height:380px;overflow-y:auto;
            '>
                {rows_html}
            </div>
        """)

    # ── Trade Signal ─────────────────────────────────────────
    _render_signal(signal)


def _render_signal(signal: dict):
    from datetime import datetime

    if not signal or signal.get("engine") == "OFFLINE" or not signal.get("direction"):
        st.html(f"""
            <div style='
                background:{_TV["panel"]};border:1px solid {_TV["border"]};
                border-radius:4px;padding:10px;margin-top:8px;
            '>
                <div style='display:flex;align-items:center;gap:6px;margin-bottom:8px;'>
                    <div style='width:2px;height:11px;background:{COLOR_ACCENT};border-radius:1px;'></div>
                    <span style='color:{_TV["text"]};font-size:10px;font-family:{_TV["font"]};font-weight:500;'>TRADE SIGNAL</span>
                </div>
                <div style='background:{_TV["bg"]};border-radius:3px;padding:12px;text-align:center;'>
                    <span style='color:{_TV["muted"]};font-size:9px;font-family:{_TV["font"]};'>Awaiting market data…</span>
                </div>
            </div>
        """)
        return

    direction = signal["direction"]
    entry     = signal["entry"]
    target    = signal["target"]
    stop      = signal["stop"]
    conf      = signal["confidence"]
    reason    = signal.get("reason", "")
    engine    = signal.get("engine", "")

    is_long     = direction == "LONG"
    dir_color   = COLOR_UP   if is_long else COLOR_DOWN
    dir_bg      = f"{COLOR_UP}0f"   if is_long else f"{COLOR_DOWN}0f"
    dir_border  = f"{COLOR_UP}35"   if is_long else f"{COLOR_DOWN}35"
    dir_icon    = "▲" if is_long else "▼"

    t_diff = target - entry
    s_diff = stop - entry
    t_pct  = (t_diff / entry) * 100 if entry else 0
    s_pct  = (s_diff / entry) * 100 if entry else 0
    rr     = abs(t_diff / s_diff) if s_diff != 0 else 0

    t_color = COLOR_UP   if t_diff >= 0 else COLOR_DOWN
    s_color = COLOR_DOWN if s_diff <= 0 else COLOR_UP

    conf_pct   = conf
    conf_color = COLOR_UP if conf >= 70 else COLOR_GOLD if conf >= 50 else _TV["muted"]

    ts = datetime.now().strftime("%H:%M")

    st.html(f"""
        <div style='
            background:{_TV["panel"]};border:1px solid {_TV["border"]};
            border-radius:4px;padding:10px;margin-top:8px;
        '>
            <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;'>
                <div style='display:flex;align-items:center;gap:6px;'>
                    <div style='width:2px;height:11px;background:{dir_color};border-radius:1px;'></div>
                    <span style='color:{_TV["text"]};font-size:10px;font-family:{_TV["font"]};font-weight:500;'>TRADE SIGNAL</span>
                </div>
                <span style='color:{_TV["dim"]};font-size:8px;font-family:{_TV["font"]};'>{engine} · {ts}</span>
            </div>

            <div style='
                background:{dir_bg};border:1px solid {dir_border};
                border-radius:3px;padding:8px 10px;margin-bottom:8px;
                display:flex;justify-content:space-between;align-items:center;
            '>
                <span style='color:{dir_color};font-family:{_TV["font"]};font-size:18px;font-weight:600;'>
                    {dir_icon} {direction}
                </span>
                <div style='text-align:right;'>
                    <div style='color:{conf_color};font-family:{_TV["font"]};font-size:13px;font-weight:600;'>{conf}%</div>
                    <div style='color:{_TV["dim"]};font-family:{_TV["font"]};font-size:8px;'>CONFIDENCE</div>
                </div>
            </div>

            <div style='background:{_TV["bg"]};border-radius:2px;height:3px;margin-bottom:8px;'>
                <div style='background:{conf_color};width:{conf_pct}%;height:3px;border-radius:2px;'></div>
            </div>

            <div style='display:flex;flex-direction:column;gap:4px;margin-bottom:8px;'>
                <div style='display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid {_TV["border"]};'>
                    <span style='color:{_TV["muted"]};font-family:{_TV["font"]};font-size:9px;'>ENTRY</span>
                    <span style='color:{_TV["text"]};font-family:{_TV["font"]};font-size:9px;font-weight:500;'>${entry:.2f}</span>
                </div>
                <div style='display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid {_TV["border"]};'>
                    <span style='color:{_TV["muted"]};font-family:{_TV["font"]};font-size:9px;'>TARGET</span>
                    <span style='font-family:{_TV["font"]};font-size:9px;'>
                        <span style='color:{t_color};font-weight:500;'>${target:.2f}</span>
                        <span style='color:{_TV["dim"]};'> {t_pct:+.2f}%</span>
                    </span>
                </div>
                <div style='display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid {_TV["border"]};'>
                    <span style='color:{_TV["muted"]};font-family:{_TV["font"]};font-size:9px;'>STOP</span>
                    <span style='font-family:{_TV["font"]};font-size:9px;'>
                        <span style='color:{s_color};font-weight:500;'>${stop:.2f}</span>
                        <span style='color:{_TV["dim"]};'> {s_pct:+.2f}%</span>
                    </span>
                </div>
                <div style='display:flex;justify-content:space-between;padding:3px 0;'>
                    <span style='color:{_TV["muted"]};font-family:{_TV["font"]};font-size:9px;'>R/R RATIO</span>
                    <span style='color:{COLOR_GOLD};font-family:{_TV["font"]};font-size:9px;font-weight:500;'>{rr:.1f} : 1</span>
                </div>
            </div>

            <div style='
                background:{_TV["bg"]};border-left:2px solid {_TV["border"]};
                padding:5px 8px;
                color:{_TV["muted"]};font-family:{_TV["font"]};font-size:8px;line-height:1.5;
                border-radius:0 2px 2px 0;
            '>{reason}</div>
        </div>
    """)


def render_trade_form(wti_price: float, signal: dict, open_trades: list):
    from data.trade_log import log_trade, close_trade

    sig_target = signal.get("target", round(wti_price * 1.012, 2)) if signal else round(wti_price * 1.012, 2)
    sig_stop   = signal.get("stop",   round(wti_price * 0.995, 2)) if signal else round(wti_price * 0.995, 2)

    st.html(f"""
        <div style='display:flex;align-items:center;gap:6px;margin-top:10px;margin-bottom:4px;'>
            <div style='width:2px;height:11px;background:{COLOR_GOLD};border-radius:1px;'></div>
            <span style='color:{_TV["text"]};font-size:10px;font-family:{_TV["font"]};font-weight:500;letter-spacing:0.5px;'>PAPER TRADE</span>
            <span style='color:{_TV["dim"]};font-size:8px;font-family:{_TV["font"]};'>MANUAL ENTRY</span>
        </div>
    """)

    with st.form("paper_trade", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        entry  = c1.number_input("ENTRY",  value=float(wti_price), format="%.2f", step=0.01)
        target = c2.number_input("TARGET", value=float(sig_target), format="%.2f", step=0.01)
        stop   = c3.number_input("STOP",   value=float(sig_stop),   format="%.2f", step=0.01)
        b1, b2 = st.columns(2)
        long_clicked  = b1.form_submit_button("▲  LONG",  use_container_width=True, type="primary")
        short_clicked = b2.form_submit_button("▼  SHORT", use_container_width=True)

    if long_clicked or short_clicked:
        direction = "LONG" if long_clicked else "SHORT"
        for t in open_trades:
            pnl_now = (wti_price - t["entry"]) if t["direction"] == "LONG" else (t["entry"] - wti_price)
            close_trade(t["id"], wti_price, "WIN" if pnl_now >= 0 else "LOSS")
        log_trade({
            "direction" : direction,
            "entry"     : entry,
            "target"    : target,
            "stop"      : stop,
            "confidence": 100,
            "reason"    : "Manual paper trade.",
            "engine"    : "MANUAL",
        })
        st.rerun()

    if open_trades:
        for trade in open_trades:
            d_color = COLOR_UP if trade["direction"] == "LONG" else COLOR_DOWN
            d_bg    = f"{COLOR_UP}0f" if trade["direction"] == "LONG" else f"{COLOR_DOWN}0f"
            d_icon  = "▲" if trade["direction"] == "LONG" else "▼"
            pnl_now = (wti_price - trade["entry"]) if trade["direction"] == "LONG" else (trade["entry"] - wti_price)
            pnl_col = COLOR_UP if pnl_now >= 0 else COLOR_DOWN
            st.html(f"""
                <div style='
                    background:{d_bg};border:1px solid {d_color}35;border-radius:3px;
                    padding:7px 10px;margin-top:6px;font-family:{_TV["font"]};
                '>
                    <div style='display:flex;justify-content:space-between;align-items:center;'>
                        <span style='color:{d_color};font-size:11px;font-weight:600;'>{d_icon} {trade["direction"]}</span>
                        <span style='color:{_TV["muted"]};font-size:9px;'>@ ${trade["entry"]:.2f}</span>
                        <span style='color:{pnl_col};font-size:13px;font-weight:600;'>{pnl_now:+.2f}</span>
                    </div>
                    <div style='color:{_TV["dim"]};font-size:8px;margin-top:3px;'>
                        TGT <span style='color:{COLOR_UP}'>${trade["target"]:.2f}</span>
                        &nbsp;·&nbsp;
                        STP <span style='color:{COLOR_DOWN}'>${trade["stop"]:.2f}</span>
                        &nbsp;·&nbsp; {trade.get("engine","")}
                    </div>
                </div>
            """)
            if st.button(f"✕  CLOSE  ·  ${wti_price:.2f}", key=f"close_{trade['id']}", use_container_width=True):
                close_trade(trade["id"], wti_price, "WIN" if pnl_now >= 0 else "LOSS")
                st.rerun()


def render_pnl_bar(stats: dict = None):
    s = stats or {}
    total    = s.get("total_pnl", 0.0)
    trades   = s.get("trade_count", 0)
    win_rate = s.get("win_rate", 0.0)
    avg_pnl  = s.get("avg_pnl", 0.0)
    max_dd   = s.get("max_dd", 0.0)
    sharpe   = s.get("sharpe")

    total_color  = COLOR_UP if total >= 0 else COLOR_DOWN
    wr_color     = COLOR_UP if win_rate >= 55 else COLOR_GOLD if win_rate >= 40 else "#ff3c3c"
    avg_color    = COLOR_UP if avg_pnl >= 0 else COLOR_DOWN
    sh_color     = COLOR_UP if (sharpe or 0) >= 1 else COLOR_GOLD if (sharpe or 0) >= 0 else "#888"

    total_str  = f"+${total:.2f}" if total >= 0 else f"-${abs(total):.2f}"
    wr_str     = f"{win_rate:.1f}%" if trades else "-"
    avg_str    = f"+${avg_pnl:.2f}" if avg_pnl >= 0 else f"-${abs(avg_pnl):.2f}" if trades else "-"
    dd_str     = f"${max_dd:.2f}" if trades else "-"
    sh_str     = str(sharpe) if sharpe is not None else "-"

    st.html(f"""
        <div style='
            background:{_TV["panel"]};border-top:1px solid {_TV["border"]};
            padding:7px 14px;font-family:"IBM Plex Mono",monospace;font-size:9px;
            display:flex;align-items:center;gap:0;margin-top:8px;flex-wrap:wrap;
        '>
            <span style='color:{_TV["muted"]};letter-spacing:0.5px;padding-right:16px;border-right:1px solid {_TV["border"]};margin-right:16px;'>
                BIN88888 · CRUDE OIL
            </span>
            <span style='padding-right:16px;border-right:1px solid {_TV["border"]};margin-right:16px;'>
                <span style='color:{_TV["dim"]};'>NET P&amp;L </span>
                <span style='color:{total_color};font-weight:600;'>{total_str}</span>
            </span>
            <span style='padding-right:16px;border-right:1px solid {_TV["border"]};margin-right:16px;'>
                <span style='color:{_TV["dim"]};'>TRADES </span>
                <span style='color:{_TV["text"]};'>{trades}</span>
            </span>
            <span style='padding-right:16px;border-right:1px solid {_TV["border"]};margin-right:16px;'>
                <span style='color:{_TV["dim"]};'>WIN% </span>
                <span style='color:{wr_color};font-weight:500;'>{wr_str}</span>
            </span>
            <span style='padding-right:16px;border-right:1px solid {_TV["border"]};margin-right:16px;'>
                <span style='color:{_TV["dim"]};'>AVG </span>
                <span style='color:{avg_color};'>{avg_str}</span>
            </span>
            <span style='padding-right:16px;border-right:1px solid {_TV["border"]};margin-right:16px;'>
                <span style='color:{_TV["dim"]};'>MAX DD </span>
                <span style='color:{COLOR_DOWN};'>{dd_str}</span>
            </span>
            <span>
                <span style='color:{_TV["dim"]};'>SHARPE </span>
                <span style='color:{sh_color};font-weight:500;'>{sh_str}</span>
            </span>
        </div>
    """)
