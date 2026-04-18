# ─────────────────────────────────────────
#  OIL TERMINAL · components/panels.py
#  Left panel (model scores) + Right panel (news placeholder)
# ─────────────────────────────────────────

import streamlit as st
from config import MODEL_SCORES, OIL_FACTORS, COLOR_UP, COLOR_DOWN, COLOR_GOLD, COLOR_ACCENT


def render_left_panel(wti_data: dict, brent_data: dict):
    """
    Renders the left sidebar panel:
    - Wallet / account info
    - Model confidence scores
    - Oil factor weights
    """

    st.html("""
        <div style='
            background:#0f0f1a;
            border:1px solid #1a1a3e;
            border-radius:6px;
            padding:12px;
            margin-bottom:10px;
        '>
            <div style='color:#888;font-size:10px;font-family:monospace;'>■ WALLET · BIN88888</div>
            <div style='color:#00ff88;font-size:11px;font-family:monospace;margin-top:4px;'>ACTIVE</div>
            <div style='color:#555;font-size:9px;font-family:monospace;margin-top:6px;'>30-DAY NET PROFIT</div>
            <div style='color:#00ff88;font-size:22px;font-family:monospace;font-weight:bold;'>+$0.00</div>
            <div style='color:#555;font-size:9px;font-family:monospace;'>SHORT/LONG · CRUDE OIL</div>
            <div style='display:flex;gap:20px;margin-top:8px;'>
                <div><div style='color:#555;font-size:9px;font-family:monospace;'>TRADES</div>
                     <div style='color:#ccc;font-size:13px;font-family:monospace;'>0</div></div>
                <div><div style='color:#555;font-size:9px;font-family:monospace;'>WINS</div>
                     <div style='color:#ccc;font-size:13px;font-family:monospace;'>0%</div></div>
                <div><div style='color:#555;font-size:9px;font-family:monospace;'>AVG R/R</div>
                     <div style='color:#ccc;font-size:13px;font-family:monospace;'>-</div></div>
            </div>
        </div>
    """)

    # ── Model Confidence ─────────────────────────────────
    st.html("""
        <div style='color:#888;font-size:10px;font-family:monospace;margin-bottom:8px;'>
            ▸ MODEL CONFIDENCE
        </div>
    """)

    for model, score in MODEL_SCORES.items():
        color = COLOR_UP if score >= 90 else COLOR_GOLD if score >= 80 else "#ff8c00"
        bar_width = score
        st.html(f"""
            <div style='margin-bottom:6px;'>
                <div style='display:flex;justify-content:space-between;'>
                    <span style='color:#aaa;font-size:9px;font-family:monospace;'>{model}</span>
                    <span style='color:{color};font-size:9px;font-family:monospace;'>{score}%</span>
                </div>
                <div style='background:#1a1a2e;border-radius:2px;height:4px;margin-top:2px;'>
                    <div style='background:{color};width:{bar_width}%;height:4px;border-radius:2px;'></div>
                </div>
            </div>
        """)

    st.html("<hr style='border-color:#1a1a2e;margin:10px 0;'>")

    # ── Oil Factor Weights ───────────────────────────────
    st.html("""
        <div style='color:#888;font-size:10px;font-family:monospace;margin-bottom:8px;'>
            ▸ OIL FACTOR WEIGHTS
        </div>
    """)

    for factor, weight in OIL_FACTORS.items():
        color = COLOR_ACCENT if weight >= 80 else COLOR_GOLD if weight >= 65 else "#888"
        st.html(f"""
            <div style='margin-bottom:6px;'>
                <div style='display:flex;justify-content:space-between;'>
                    <span style='color:#aaa;font-size:9px;font-family:monospace;'>{factor}</span>
                    <span style='color:{color};font-size:9px;font-family:monospace;'>{weight}%</span>
                </div>
                <div style='background:#1a1a2e;border-radius:2px;height:3px;margin-top:2px;'>
                    <div style='background:{color};width:{weight}%;height:3px;border-radius:2px;'></div>
                </div>
            </div>
        """)


def render_right_panel(news_items: list = None, signal: dict = None):
    if news_items is None:
        news_items = []

    tag_colors = {
        "BULL"   : ("#00ff88", "#0a2e1a"),
        "BEAR"   : ("#ff3c3c", "#2e0a0a"),
        "NEUTRAL": ("#ffd700", "#2e2a00"),
    }

    gemini_active = bool(__import__("config").GEMINI_API_KEY)
    engine_label  = "GEMINI·TAGGED" if gemini_active else "KEYWORD·TAGGED"
    count_label   = f"{len(news_items)} headlines" if news_items else "no data"

    header = f"""
        <div style='
            background:#0f0f1a;
            border:1px solid #1a1a3e;
            border-radius:6px 6px 0 0;
            padding:8px 12px 6px;
        '>
            <div style='display:flex;justify-content:space-between;align-items:center;'>
                <span style='color:#888;font-size:10px;font-family:monospace;'>■ OSINT · NEWS SCANNER</span>
                <span style='color:#333;font-size:8px;font-family:monospace;'>{engine_label}</span>
            </div>
            <div style='color:#333;font-size:8px;font-family:monospace;margin-top:2px;'>
                {count_label} · 5m cache · OilPrice · Yahoo · MarketWatch
            </div>
        </div>
    """
    st.html(header)

    if not news_items:
        st.html("""
            <div style='
                background:#0f0f1a;border:1px solid #1a1a3e;border-top:none;
                border-radius:0 0 6px 6px;padding:20px 12px;text-align:center;
            '>
                <span style='color:#333;font-size:10px;font-family:monospace;'>
                    ── no headlines loaded ──
                </span>
            </div>
        """)
    else:
        rows_html = ""
        for item in news_items:
            tag   = item.get("tag", "NEUTRAL")
            color, bg = tag_colors.get(tag, tag_colors["NEUTRAL"])
            title = item["title"]
            short = title if len(title) <= 58 else title[:55] + "…"
            src   = item.get("source", "")
            rows_html += f"""
                <div style='
                    padding:7px 12px;
                    border-bottom:1px solid #111122;
                '>
                    <div style='display:flex;align-items:flex-start;gap:6px;'>
                        <span style='
                            background:{bg};color:{color};
                            font-family:monospace;font-size:7px;font-weight:bold;
                            padding:1px 4px;border-radius:2px;border:1px solid {color}33;
                            white-space:nowrap;margin-top:1px;flex-shrink:0;
                        '>{tag}</span>
                        <span style='color:#bbb;font-family:monospace;font-size:9px;line-height:1.4;'>
                            {short}
                        </span>
                    </div>
                    <div style='color:#333;font-family:monospace;font-size:8px;margin-top:3px;padding-left:44px;'>
                        {src}
                    </div>
                </div>
            """

        st.html(f"""
            <div style='
                background:#0a0a12;border:1px solid #1a1a3e;border-top:none;
                border-radius:0 0 6px 6px;max-height:420px;overflow-y:auto;
            '>
                {rows_html}
            </div>
        """)

    # ── Trade Signal ─────────────────────────────────────────
    _render_signal(signal)


def _render_signal(signal: dict):
    from datetime import datetime

    if not signal or signal.get("engine") == "OFFLINE" or not signal.get("direction"):
        st.html("""
            <div style='
                background:#0f0f1a;border:1px solid #1a1a3e;
                border-radius:6px;padding:12px;margin-top:10px;
            '>
                <div style='color:#888;font-size:10px;font-family:monospace;'>
                    ■ TRADE SIGNAL · LIVE PREDICTION
                </div>
                <div style='
                    background:#1a1a2e;border-radius:4px;padding:10px;
                    margin-top:10px;text-align:center;
                '>
                    <div style='color:#333;font-size:10px;font-family:monospace;'>
                        NO MARKET DATA
                    </div>
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
    dir_color   = "#00ff88" if is_long else "#ff3c3c"
    dir_bg      = "#0a2e1a" if is_long else "#2e0a0a"
    dir_border  = "#00ff8833" if is_long else "#ff3c3c33"
    dir_icon    = "▲" if is_long else "▼"

    t_diff = target - entry
    s_diff = stop - entry
    t_pct  = (t_diff / entry) * 100 if entry else 0
    s_pct  = (s_diff / entry) * 100 if entry else 0
    rr     = abs(t_diff / s_diff) if s_diff != 0 else 0

    t_color = "#00ff88" if t_diff >= 0 else "#ff3c3c"
    s_color = "#ff3c3c" if s_diff <= 0 else "#00ff88"

    conf_filled = conf // 10
    conf_bar    = "█" * conf_filled + "░" * (10 - conf_filled)
    conf_color  = "#00ff88" if conf >= 70 else COLOR_GOLD if conf >= 50 else "#888"

    ts = datetime.now().strftime("%H:%M")

    st.html(f"""
        <div style='
            background:#0f0f1a;border:1px solid #1a1a3e;
            border-radius:6px;padding:12px;margin-top:10px;
        '>
            <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;'>
                <span style='color:#888;font-size:10px;font-family:monospace;'>■ TRADE SIGNAL</span>
                <span style='color:#333;font-size:8px;font-family:monospace;'>{engine}</span>
            </div>

            <div style='
                background:{dir_bg};border:1px solid {dir_border};
                border-radius:4px;padding:8px 12px;margin-bottom:10px;
                display:flex;justify-content:space-between;align-items:center;
            '>
                <span style='color:{dir_color};font-family:monospace;font-size:16px;font-weight:bold;'>
                    {dir_icon} {direction}
                </span>
                <span style='color:{conf_color};font-family:monospace;font-size:10px;'>
                    {conf}% CONF
                </span>
            </div>

            <div style='
                font-family:monospace;font-size:8px;color:{conf_color};
                letter-spacing:0.5px;margin-bottom:10px;
            '>{conf_bar}</div>

            <div style='margin-bottom:4px;display:flex;justify-content:space-between;'>
                <span style='color:#555;font-family:monospace;font-size:9px;'>ENTRY</span>
                <span style='color:#ccc;font-family:monospace;font-size:9px;'>${entry:.2f}</span>
            </div>
            <div style='margin-bottom:4px;display:flex;justify-content:space-between;'>
                <span style='color:#555;font-family:monospace;font-size:9px;'>TARGET</span>
                <span style='font-family:monospace;font-size:9px;'>
                    <span style='color:{t_color};'>${target:.2f}</span>
                    <span style='color:#333;'> {t_pct:+.2f}%</span>
                </span>
            </div>
            <div style='margin-bottom:4px;display:flex;justify-content:space-between;'>
                <span style='color:#555;font-family:monospace;font-size:9px;'>STOP</span>
                <span style='font-family:monospace;font-size:9px;'>
                    <span style='color:{s_color};'>${stop:.2f}</span>
                    <span style='color:#333;'> {s_pct:+.2f}%</span>
                </span>
            </div>
            <div style='margin-bottom:10px;display:flex;justify-content:space-between;'>
                <span style='color:#555;font-family:monospace;font-size:9px;'>R/R</span>
                <span style='color:#ffd700;font-family:monospace;font-size:9px;'>{rr:.1f}:1</span>
            </div>

            <div style='
                background:#0a0a14;border-radius:3px;padding:6px 8px;
                color:#444;font-family:monospace;font-size:8px;line-height:1.5;
                margin-bottom:6px;
            '>{reason}</div>

            <div style='color:#222;font-family:monospace;font-size:8px;'>
                GENERATED &middot; {ts}
            </div>
        </div>
    """)


def render_trade_form(wti_price: float, signal: dict, open_trades: list):
    from data.trade_log import log_trade, close_trade

    sig_target = signal.get("target", round(wti_price * 1.012, 2)) if signal else round(wti_price * 1.012, 2)
    sig_stop   = signal.get("stop",   round(wti_price * 0.995, 2)) if signal else round(wti_price * 0.995, 2)

    st.html("<div style='color:#888;font-family:monospace;font-size:10px;margin-top:10px;letter-spacing:1px;'>■ PAPER TRADE · MANUAL ENTRY</div>")

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
            d_icon  = "▲" if trade["direction"] == "LONG" else "▼"
            pnl_now = (wti_price - trade["entry"]) if trade["direction"] == "LONG" else (trade["entry"] - wti_price)
            pnl_col = COLOR_UP if pnl_now >= 0 else COLOR_DOWN
            st.html(f"""
                <div style='
                    background:#0f0f1a;border:1px solid #1a1a3e;border-radius:4px;
                    padding:8px 10px;margin-top:6px;font-family:monospace;
                '>
                    <div style='display:flex;justify-content:space-between;align-items:center;'>
                        <span style='color:{d_color};font-size:12px;font-weight:bold;'>{d_icon} {trade["direction"]} @ ${trade["entry"]:.2f}</span>
                        <span style='color:{pnl_col};font-size:13px;font-weight:bold;'>{pnl_now:+.2f}</span>
                    </div>
                    <div style='color:#333;font-size:8px;margin-top:3px;'>
                        TGT ${trade["target"]:.2f} &nbsp;·&nbsp; STP ${trade["stop"]:.2f} &nbsp;·&nbsp; {trade.get("engine","")}
                    </div>
                </div>
            """)
            if st.button(f"CLOSE AT MARKET  ·  ${wti_price:.2f}", key=f"close_{trade['id']}", use_container_width=True):
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
            background:#0a0a14;border-top:1px solid #1a1a3e;
            padding:8px 16px;font-family:monospace;font-size:10px;color:#333;
            display:flex;gap:24px;margin-top:10px;flex-wrap:wrap;
        '>
            <span style='color:#1a1a3e;'>BIN88888 · PNL HISTORY · CRUDE OIL</span>
            <span>TOTAL <span style='color:{total_color};'>{total_str}</span></span>
            <span>TRADES <span style='color:#555;'>{trades}</span></span>
            <span>WIN <span style='color:{wr_color};'>{wr_str}</span></span>
            <span>AVG <span style='color:{avg_color};'>{avg_str}</span></span>
            <span>MAX DD <span style='color:#ff3c3c;'>{dd_str}</span></span>
            <span>SHARPE <span style='color:{sh_color};'>{sh_str}</span></span>
        </div>
    """)
