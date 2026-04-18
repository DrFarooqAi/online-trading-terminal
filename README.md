# 🛢️ ONLINE TRADING TERMINAL

**Live Crude Oil AI Prediction Terminal — Free to Use**

## 🚀 Try It Live — No Installation Needed

**👉 [https://online-trading-terminal-drfarooq.streamlit.app/](https://online-trading-terminal-drfarooq.streamlit.app/)**

Open in any browser. 100% free.

---

## 📊 Features

| Feature | Description |
|---|---|
| **Live Prices** | WTI Crude + Brent — real-time via Yahoo Finance |
| **Candlestick Chart** | 5-min candles with volume |
| **OSINT News Scanner** | RSS headlines tagged BULL / BEAR / NEUTRAL |
| **MiroFish Graph** | D3.js force-directed relationship network |
| **AI Signal** | LONG / SHORT with entry, target, stop, confidence % |
| **Paper Trading** | Manual paper trade with live P&L tracking |
| **Equity Curve** | SQLite trade log + win rate + Sharpe ratio |

---

## 🗺️ Roadmap

| Phase | Feature | Status |
|---|---|---|
| Phase 1 | Live chart + dark terminal UI | ✅ Done |
| Phase 2 | OSINT news scanner + sentiment tagging | ✅ Done |
| Phase 3 | MiroFish relationship graph (D3.js) | ✅ Done |
| Phase 4 | AI signal generator (Gemini / rule-based) | ✅ Done |
| Phase 5 | PnL tracker + paper trading | ✅ Done |

---

## ⚡ Run Locally

```bash
git clone https://github.com/DrFarooqAi/online-trading-terminal.git
cd online-trading-terminal
pip install -r requirements.txt
streamlit run app.py
```

---

## 🤖 Enable Gemini AI Signals (Optional — Free)

1. Get a free API key at [aistudio.google.com](https://aistudio.google.com)
2. Open `config.py` and paste your key:
```python
GEMINI_API_KEY = "AIza..."
```

---

## 💰 Cost
$0/month — 100% free open-source stack.
`yfinance · Streamlit · Plotly · D3.js · feedparser · SQLite`
