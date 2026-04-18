# ─────────────────────────────────────────
#  OIL TERMINAL · components/chart.py
#  Builds the Plotly candlestick chart
# ─────────────────────────────────────────

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from config import COLOR_UP, COLOR_DOWN, COLOR_BG, COLOR_PANEL, COLOR_ACCENT, COLOR_TEXT


def build_candlestick_chart(df: pd.DataFrame, ticker_label: str = "WTI CRUDE · 5M") -> go.Figure:
    """
    Builds a dark-themed candlestick chart with volume bars below.
    """
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor=COLOR_BG,
            plot_bgcolor=COLOR_PANEL,
            font=dict(color=COLOR_TEXT),
            title="No data available"
        )
        return fig

    # Flatten MultiIndex columns if present (yfinance quirk)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Create subplot: top = candles, bottom = volume
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=[0.75, 0.25]
    )

    # ── Candlestick ──────────────────────────────────────
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            increasing_line_color=COLOR_UP,
            decreasing_line_color=COLOR_DOWN,
            increasing_fillcolor=COLOR_UP,
            decreasing_fillcolor=COLOR_DOWN,
            line_width=1,
            name=ticker_label,
        ),
        row=1, col=1
    )

    # ── Volume Bars ──────────────────────────────────────
    colors = [
        COLOR_UP if df["Close"].iloc[i] >= df["Open"].iloc[i] else COLOR_DOWN
        for i in range(len(df))
    ]

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["Volume"],
            marker_color=colors,
            marker_opacity=0.6,
            name="Volume",
            showlegend=False,
        ),
        row=2, col=1
    )

    # ── Current price line ───────────────────────────────
    last_price = float(df["Close"].iloc[-1])
    fig.add_hline(
        y=last_price,
        line_dash="dash",
        line_color=COLOR_ACCENT,
        line_width=1,
        annotation_text=f" ${last_price:.2f}",
        annotation_font_color=COLOR_ACCENT,
        annotation_position="right",
        row=1, col=1
    )

    # ── Layout ───────────────────────────────────────────
    fig.update_layout(
        paper_bgcolor=COLOR_BG,
        plot_bgcolor=COLOR_PANEL,
        font=dict(color=COLOR_TEXT, family="monospace", size=11),
        margin=dict(l=10, r=60, t=30, b=10),
        xaxis_rangeslider_visible=False,
        showlegend=False,
        title=dict(
            text=f"<b>{ticker_label}</b>",
            font=dict(color=COLOR_ACCENT, size=13),
            x=0.01
        ),
        xaxis2=dict(
            showgrid=True,
            gridcolor="#1a1a2e",
            tickfont=dict(color=COLOR_TEXT, size=9),
            tickformat="%H:%M\n%d %b",
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#1a1a2e",
            tickfont=dict(color=COLOR_TEXT, size=10),
            tickprefix="$",
            side="right",
        ),
        yaxis2=dict(
            showgrid=False,
            tickfont=dict(color=COLOR_TEXT, size=9),
            side="right",
        ),
        hoverlabel=dict(
            bgcolor=COLOR_PANEL,
            font_color=COLOR_TEXT,
            font_family="monospace"
        ),
    )

    # Grid styling
    fig.update_xaxes(showgrid=True, gridcolor="#1a1a2e", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#1a1a2e", zeroline=False)

    return fig
