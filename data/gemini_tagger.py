import streamlit as st
from config import GEMINI_API_KEY


@st.cache_data(ttl=300)
def tag_headlines(headlines: tuple) -> dict:
    """
    Returns {headline_text: "BULL"|"BEAR"|"NEUTRAL"}.
    Falls back to keyword scoring when API key is absent.
    """
    if not headlines:
        return {}

    if GEMINI_API_KEY:
        return _tag_via_gemini(headlines)
    return _tag_via_keywords(headlines)


def _tag_via_gemini(headlines: tuple) -> dict:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")

        numbered = "\n".join(f"{i+1}. {h}" for i, h in enumerate(headlines))
        prompt = (
            "You are an oil market analyst. For each headline, reply with ONLY "
            "the line number and one tag (BULL, BEAR, or NEUTRAL) for its likely "
            "impact on WTI crude oil price. Format exactly: '1. BULL'\n\n"
            + numbered
        )

        response = model.generate_content(prompt)
        tags = {}
        for line in response.text.strip().splitlines():
            line = line.strip()
            for tag in ("BULL", "BEAR", "NEUTRAL"):
                if tag in line.upper():
                    parts = line.split(".")
                    try:
                        idx = int(parts[0].strip()) - 1
                        if 0 <= idx < len(headlines):
                            tags[headlines[idx]] = tag
                    except (ValueError, IndexError):
                        pass
                    break

        for h in headlines:
            tags.setdefault(h, "NEUTRAL")
        return tags

    except Exception:
        return _tag_via_keywords(headlines)


_BULL_WORDS = {
    "cut", "cuts", "shortage", "supply cut", "opec", "geopolit",
    "iran", "sanction", "hurricane", "disruption", "surge", "rally",
    "rise", "rises", "rising", "jumps", "gain", "gains",
}
_BEAR_WORDS = {
    "increase output", "raise output", "output hike", "glut", "surplus",
    "recession", "demand falls", "demand drop", "inventory build",
    "build", "oversupply", "fall", "falls", "drop", "drops", "decline",
    "declines", "slump", "weak", "weakens",
}


def _tag_via_keywords(headlines: tuple) -> dict:
    tags = {}
    for h in headlines:
        lower = h.lower()
        bull = sum(1 for w in _BULL_WORDS if w in lower)
        bear = sum(1 for w in _BEAR_WORDS if w in lower)
        if bull > bear:
            tags[h] = "BULL"
        elif bear > bull:
            tags[h] = "BEAR"
        else:
            tags[h] = "NEUTRAL"
    return tags
