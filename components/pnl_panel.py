import streamlit as st
import plotly.graph_objects as go
from config import COLOR_BG, COLOR_UP, COLOR_DOWN, COLOR_ACCENT, COLOR_GOLD, COLOR_PANEL, COLOR_TEXT

_TV = {
    "bg"    : "#131722",
    "panel" : "#1e222d",
    "border": "#2a2e39",
    "text"  : "#d1d4dc",
    "muted" : "#787b86",
    "dim"   : "#4a4e5a",
    "font"  : "'IBM Plex Mono', monospace",
}


def render_pnl_panel(stats: dict, trades: list):
    st.html(f"""
        <div style='display:flex;align-items:center;gap:8px;padding:8px 4px 5px;border-top:1px solid {_TV["border"]};margin-top:4px;'>
            <div style='width:3px;height:14px;background:{COLOR_ACCENT};border-radius:2px;'></div>
            <span style='color:{_TV["text"]};font-family:{_TV["font"]};font-size:10px;font-weight:600;letter-spacing:0.5px;'>PNL TRACKER</span>
            <span style='color:{_TV["dim"]};font-family:{_TV["font"]};font-size:9px;'>EQUITY CURVE · TRADE LOG</span>
            <div style='flex:1;height:1px;background:{_TV["border"]};'></div>
        </div>
    """)

    eq_col, table_col = st.columns([3, 2])

    with eq_col:
        _render_equity_curve(stats)

    with table_col:
        _render_trade_table(trades, stats)


def _render_equity_curve(stats: dict):
    curve = stats.get("equity_curve", [])
    ticks = stats.get("equity_timestamps", [])

    fig = go.Figure()

    if not curve:
        fig.add_annotation(
            text="NO CLOSED TRADES YET · AUTO-LOGS WHEN SIGNAL CHANGES",
            xref="paper", yref="paper", x=0.5, y=0.5,
            font=dict(color="#888", family="monospace", size=10),
            showarrow=False,
        )
    else:
        final_positive = curve[-1] >= 0
        fill_color = "rgba(0,255,136,0.07)" if final_positive else "rgba(255,60,60,0.07)"
        line_color  = COLOR_UP if final_positive else COLOR_DOWN

        x = ticks if ticks and len(ticks) == len(curve) else list(range(1, len(curve) + 1))

        fig.add_trace(go.Scatter(
            x=x, y=curve,
            fill="tozeroy", fillcolor=fill_color,
            line=dict(color=line_color, width=2),
            mode="lines+markers",
            marker=dict(size=4, color=line_color),
            hovertemplate="Trade %{x}<br>PnL: $%{y:.2f}<extra></extra>",
        ))
        fig.add_hline(y=0, line_dash="dash", line_color="#1a1a2e", line_width=1)

    final_pnl   = stats.get("total_pnl", 0)
    pnl_color   = COLOR_UP if final_pnl >= 0 else COLOR_DOWN
    pnl_sign    = "+" if final_pnl >= 0 else ""

    fig.update_layout(
        paper_bgcolor=_TV["bg"], plot_bgcolor=_TV["panel"],
        margin=dict(l=0, r=52, t=28, b=0), height=190,
        showlegend=False,
        title=dict(
            text=f"EQUITY CURVE &nbsp;&nbsp;<span style='color:{pnl_color};font-weight:600'>{pnl_sign}${final_pnl:.2f}</span>",
            font=dict(color=_TV["muted"], size=9, family="'IBM Plex Mono', monospace"), x=0.01,
        ),
        xaxis=dict(
            showgrid=True, gridcolor=_TV["border"],
            tickfont=dict(color=_TV["dim"], size=8, family="'IBM Plex Mono', monospace"),
            linecolor=_TV["border"], zeroline=False,
        ),
        yaxis=dict(
            showgrid=True, gridcolor=_TV["border"],
            tickfont=dict(color=_TV["muted"], size=9, family="'IBM Plex Mono', monospace"),
            tickprefix="$", side="right",
            linecolor=_TV["border"], zeroline=False,
        ),
        hoverlabel=dict(
            bgcolor=_TV["panel"], bordercolor=_TV["border"],
            font_color=_TV["text"], font_family="'IBM Plex Mono', monospace",
        ),
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _render_trade_table(trades: list, stats: dict):
    win_rate = stats.get("win_rate", 0)
    sharpe   = stats.get("sharpe")
    max_dd   = stats.get("max_dd", 0)

    wr_color  = COLOR_UP if win_rate >= 55 else COLOR_GOLD if win_rate >= 40 else "#ff3c3c"
    sh_color  = COLOR_UP if (sharpe or 0) >= 1 else COLOR_GOLD if (sharpe or 0) >= 0 else "#ff3c3c"

    st.html(f"""
        <div style='
            background:{_TV["panel"]};border:1px solid {_TV["border"]};
            border-radius:4px;padding:8px 10px;
            font-family:{_TV["font"]};font-size:8px;
            display:flex;gap:16px;margin-bottom:6px;flex-wrap:wrap;
        '>
            <div>
                <div style='color:{_TV["muted"]};'>WIN RATE</div>
                <div style='color:{wr_color};font-size:13px;font-weight:bold;'>{win_rate:.1f}%</div>
            </div>
            <div>
                <div style='color:{_TV["muted"]};'>SHARPE</div>
                <div style='color:{sh_color};font-size:13px;font-weight:bold;'>{sharpe if sharpe is not None else "--"}</div>
            </div>
            <div>
                <div style='color:{_TV["muted"]};'>MAX DD</div>
                <div style='color:{COLOR_DOWN};font-size:13px;font-weight:bold;'>${max_dd:.2f}</div>
            </div>
            <div>
                <div style='color:{_TV["muted"]};'>TRADES</div>
                <div style='color:{_TV["text"]};font-size:13px;font-weight:bold;'>{stats.get("trade_count", 0)}</div>
            </div>
        </div>
    """)

    if not trades:
        st.html(f"""
            <div style='background:{_TV["bg"]};border:1px solid {_TV["border"]};border-radius:4px;
                        padding:20px;text-align:center;height:130px;
                        display:flex;align-items:center;justify-content:center;'>
                <span style='color:{_TV["muted"]};font-family:{_TV["font"]};font-size:9px;'>── no trades yet ──</span>
            </div>
        """)
        return

    rows_html = ""
    for t in trades[:8]:
        d_color  = COLOR_UP if t["direction"] == "LONG" else COLOR_DOWN
        d_icon   = "▲" if t["direction"] == "LONG" else "▼"
        pnl      = t.get("pnl")
        pnl_str  = f"${pnl:+.2f}" if pnl is not None else "--"
        pnl_col  = COLOR_UP if (pnl or 0) > 0 else COLOR_DOWN if (pnl or 0) < 0 else "#444"
        r_col    = COLOR_UP if t["result"] == "WIN" else COLOR_DOWN if t["result"] == "LOSS" else "#444"
        r_txt    = t["result"]
        time_str = t["opened_at"][11:16] if t.get("opened_at") else "--"

        rows_html += f"""
            <tr style='border-bottom:1px solid {_TV["bg"]};'>
                <td style='color:{_TV["dim"]};font-size:8px;padding:3px 4px;font-family:{_TV["font"]};'>{time_str}</td>
                <td style='color:{d_color};font-size:8px;padding:3px 4px;'>{d_icon}</td>
                <td style='color:{_TV["muted"]};font-size:8px;padding:3px 4px;font-family:{_TV["font"]};'>${t["entry"]:.2f}</td>
                <td style='color:{pnl_col};font-size:8px;padding:3px 4px;font-family:{_TV["font"]};'>{pnl_str}</td>
                <td style='color:{r_col};font-size:8px;padding:3px 4px;font-family:{_TV["font"]};font-weight:bold;'>{r_txt}</td>
            </tr>
        """

    st.html(f"""
        <div style='background:{_TV["bg"]};border:1px solid {_TV["border"]};border-radius:4px;
                    padding:6px 8px;overflow-y:auto;max-height:140px;'>
            <table style='width:100%;border-collapse:collapse;font-family:{_TV["font"]};'>
                <tr>
                    <th style='color:{_TV["dim"]};font-size:8px;text-align:left;padding:2px 4px;'>TIME</th>
                    <th style='color:{_TV["dim"]};font-size:8px;text-align:left;padding:2px 4px;'>D</th>
                    <th style='color:{_TV["dim"]};font-size:8px;text-align:left;padding:2px 4px;'>ENTRY</th>
                    <th style='color:{_TV["dim"]};font-size:8px;text-align:left;padding:2px 4px;'>PNL</th>
                    <th style='color:{_TV["dim"]};font-size:8px;text-align:left;padding:2px 4px;'>RES</th>
                </tr>
                {rows_html}
            </table>
        </div>
    """)
