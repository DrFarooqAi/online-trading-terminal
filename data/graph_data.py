from config import OIL_FACTORS

GRAPH_NODES = [
    {"id": "WTI",    "label": "WTI PRICE",    "type": "center", "weight": 100},
    {"id": "OPEC",   "label": "OPEC+",        "type": "supply", "weight": OIL_FACTORS["OPEC+"]},
    {"id": "USD",    "label": "USD / DXY",    "type": "macro",  "weight": OIL_FACTORS["USD/DXY"]},
    {"id": "INV",    "label": "INVENTORY",    "type": "supply", "weight": OIL_FACTORS["INVENTORY"]},
    {"id": "GEO",    "label": "GEOPOLITICAL", "type": "risk",   "weight": OIL_FACTORS["GEOPOL"]},
    {"id": "CHINA",  "label": "CHINA PMI",    "type": "demand", "weight": OIL_FACTORS["CHINA PMI"]},
    {"id": "REF",    "label": "REFINERIES",   "type": "demand", "weight": OIL_FACTORS["REFINERIES"]},
    {"id": "FED",    "label": "FED RATE",     "type": "macro",  "weight": 70},
    {"id": "DEMAND", "label": "GLOBAL DEMAND","type": "demand", "weight": 72},
]

GRAPH_LINKS = [
    {"source": "OPEC",   "target": "WTI",    "direction": "bull", "strength": OIL_FACTORS["OPEC+"]},
    {"source": "USD",    "target": "WTI",    "direction": "bear", "strength": OIL_FACTORS["USD/DXY"]},
    {"source": "INV",    "target": "WTI",    "direction": "bear", "strength": OIL_FACTORS["INVENTORY"]},
    {"source": "GEO",    "target": "WTI",    "direction": "bull", "strength": OIL_FACTORS["GEOPOL"]},
    {"source": "CHINA",  "target": "WTI",    "direction": "bull", "strength": OIL_FACTORS["CHINA PMI"]},
    {"source": "REF",    "target": "DEMAND", "direction": "bull", "strength": OIL_FACTORS["REFINERIES"]},
    {"source": "DEMAND", "target": "WTI",    "direction": "bull", "strength": 72},
    {"source": "FED",    "target": "USD",    "direction": "bull", "strength": 70},
    {"source": "OPEC",   "target": "INV",    "direction": "bear", "strength": 55},
]


def get_graph_data() -> dict:
    return {"nodes": GRAPH_NODES, "links": GRAPH_LINKS}


def get_convergence_score(links: list) -> dict:
    wti_links  = [l for l in links if l["target"] == "WTI"]
    bull_str   = sum(l["strength"] for l in wti_links if l["direction"] == "bull")
    bear_str   = sum(l["strength"] for l in wti_links if l["direction"] == "bear")
    total      = bull_str + bear_str or 1
    score      = round((bull_str - bear_str) / total * 100)
    bull_count = sum(1 for l in wti_links if l["direction"] == "bull")
    bear_count = sum(1 for l in wti_links if l["direction"] == "bear")
    direction  = "BULLISH" if score >= 20 else "BEARISH" if score <= -20 else "NEUTRAL"
    return {
        "score"      : score,
        "bull_count" : bull_count,
        "bear_count" : bear_count,
        "bull_str"   : bull_str,
        "bear_str"   : bear_str,
        "direction"  : direction,
    }
