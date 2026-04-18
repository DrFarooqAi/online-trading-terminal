import re
import streamlit as st
from config import GEMINI_API_KEY


@st.cache_data(ttl=300)
def get_trade_signal(
    wti_price: float,
    wti_change: float,
    brent_price: float,
    convergence_score: int,
    convergence_dir: str,
    bull_strength: int,
    bear_strength: int,
    news_bull: int,
    news_bear: int,
    top_headlines: tuple,
) -> dict:
    if wti_price <= 0:
        return _offline_signal()

    if GEMINI_API_KEY:
        result = _gemini_signal(
            wti_price, wti_change, brent_price,
            convergence_score, convergence_dir,
            bull_strength, bear_strength,
            news_bull, news_bear, top_headlines,
        )
        if result:
            return result

    return _rule_based_signal(
        wti_price, convergence_score, convergence_dir,
        bull_strength, bear_strength, news_bull, news_bear,
    )


def _gemini_signal(wti_price, wti_change, brent_price,
                   conv_score, conv_dir, bull_str, bear_str,
                   news_bull, news_bear, top_headlines):
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")

        hl_text = "\n".join(f"  [{tag}] {title}" for tag, title in top_headlines) \
                  or "  No recent headlines."

        prompt = (
            "You are an expert WTI crude oil futures intraday trader.\n\n"
            "MARKET DATA:\n"
            f"- WTI Price: ${wti_price:.2f} (change: {wti_change:+.2f})\n"
            f"- Brent Price: ${brent_price:.2f}\n\n"
            "MIROFISH GRAPH CONVERGENCE:\n"
            f"- Direction: {conv_dir}\n"
            f"- Score: {conv_score:+d}\n"
            f"- Bull strength: {bull_str} | Bear strength: {bear_str}\n\n"
            "NEWS SENTIMENT (recent headlines):\n"
            f"- BULL: {news_bull} | BEAR: {news_bear}\n"
            f"Top headlines:\n{hl_text}\n\n"
            "Generate ONE intraday trade signal for WTI crude oil futures.\n"
            "Reply in EXACTLY this format, nothing else:\n"
            "DIRECTION: LONG\n"
            "ENTRY: $XX.XX\n"
            "TARGET: $XX.XX\n"
            "STOP: $XX.XX\n"
            "CONFIDENCE: XX%\n"
            "REASON: One sentence."
        )

        response = model.generate_content(prompt)
        return _parse_response(response.text)
    except Exception:
        return None


def _parse_response(text: str) -> dict | None:
    try:
        direction  = re.search(r"DIRECTION:\s*(LONG|SHORT)", text, re.I)
        entry      = re.search(r"ENTRY:\s*\$?([\d.]+)", text, re.I)
        target     = re.search(r"TARGET:\s*\$?([\d.]+)", text, re.I)
        stop       = re.search(r"STOP:\s*\$?([\d.]+)", text, re.I)
        confidence = re.search(r"CONFIDENCE:\s*(\d+)", text, re.I)
        reason     = re.search(r"REASON:\s*(.+)", text, re.I)

        if not all([direction, entry, target, stop, confidence]):
            return None

        return {
            "direction" : direction.group(1).upper(),
            "entry"     : float(entry.group(1)),
            "target"    : float(target.group(1)),
            "stop"      : float(stop.group(1)),
            "confidence": min(int(confidence.group(1)), 99),
            "reason"    : reason.group(1).strip() if reason else "",
            "engine"    : "GEMINI",
        }
    except Exception:
        return None


def _rule_based_signal(price, conv_score, conv_dir, bull_str, bear_str, news_bull, news_bear):
    if conv_dir == "BULLISH" or (conv_dir == "NEUTRAL" and news_bull >= news_bear):
        direction = "LONG"
    else:
        direction = "SHORT"

    entry = round(price, 2)
    if direction == "LONG":
        target = round(price * 1.012, 2)
        stop   = round(price * 0.995, 2)
    else:
        target = round(price * 0.988, 2)
        stop   = round(price * 1.005, 2)

    conv_conf  = min(abs(conv_score) * 0.3, 25)
    aligned_n  = news_bull if direction == "LONG" else news_bear
    news_conf  = min(aligned_n * 2, 15)
    confidence = min(int(45 + conv_conf + news_conf), 92)

    total_str = bull_str + bear_str or 1
    aligned_s = bull_str if direction == "LONG" else bear_str
    reason = (
        f"Graph {conv_dir.lower()} ({conv_score:+d}). "
        f"Signal strength {aligned_s}/{total_str}."
    )

    return {
        "direction" : direction,
        "entry"     : entry,
        "target"    : target,
        "stop"      : stop,
        "confidence": confidence,
        "reason"    : reason,
        "engine"    : "RULE-BASED",
    }


def _offline_signal() -> dict:
    return {
        "direction" : None,
        "entry"     : 0.0,
        "target"    : 0.0,
        "stop"      : 0.0,
        "confidence": 0,
        "reason"    : "No market data.",
        "engine"    : "OFFLINE",
    }
