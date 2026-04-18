# 🛢️ OIL TERMINAL · OPUS 4.7
**Crude Oil Prediction Terminal — Phase 1**

---

## ⚡ Quick Start

### Step 1 — Copy project to E drive
Place this entire folder at:
```
E:\oil_terminal\
```

### Step 2 — Open PowerShell and navigate
```powershell
cd E:\oil_terminal
```

### Step 3 — Activate Conda base
```powershell
C:\Users\ac\miniconda3\Scripts\activate.bat base
```

### Step 4 — Install dependencies
```powershell
pip install -r requirements.txt
```

### Step 5 — Run the app
```powershell
streamlit run app.py
```

### Step 6 — Open in browser
```
http://localhost:8501
```

---

## 📁 File Structure
```
oil_terminal/
├── app.py                    ← Main app (run this)
├── config.py                 ← All settings here
├── requirements.txt          ← Dependencies
├── data/
│   ├── __init__.py
│   └── price_feed.py         ← yfinance WTI/Brent data
└── components/
    ├── __init__.py
    ├── chart.py              ← Candlestick chart builder
    └── panels.py             ← Left/right panels + PnL bar
```

---

## 🗺️ Roadmap
| Phase | Feature | Status |
|---|---|---|
| Phase 1 | Live chart + dashboard shell | ✅ Done |
| Phase 2 | OSINT news scanner + Gemini tagging | ⏳ Next |
| Phase 3 | MiroFish relationship graph (D3.js) | ⏳ Planned |
| Phase 4 | AI signal generator (entry/target/stop) | ⏳ Planned |
| Phase 5 | PnL tracker + React migration | ⏳ Planned |

---

## ⚠️ Notes
- yfinance data has ~15 minute delay (free tier)
- 5-min candles available for last 5 days only
- App auto-refreshes every 60 seconds
- All settings in `config.py`
