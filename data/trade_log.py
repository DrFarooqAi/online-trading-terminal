import sqlite3
import os
import statistics
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "trades.db")


def _conn():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    with _conn() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                opened_at   TEXT NOT NULL,
                direction   TEXT NOT NULL,
                entry       REAL NOT NULL,
                target      REAL NOT NULL,
                stop        REAL NOT NULL,
                confidence  INTEGER NOT NULL,
                engine      TEXT NOT NULL,
                result      TEXT DEFAULT 'OPEN',
                exit_price  REAL DEFAULT NULL,
                pnl         REAL DEFAULT NULL,
                closed_at   TEXT DEFAULT NULL
            )
        """)


def log_trade(signal: dict) -> int:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with _conn() as con:
        cur = con.execute(
            """INSERT INTO trades (opened_at, direction, entry, target, stop, confidence, engine)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (ts, signal["direction"], signal["entry"], signal["target"],
             signal["stop"], signal["confidence"], signal.get("engine", "")),
        )
        return cur.lastrowid


def close_trade(trade_id: int, exit_price: float, result: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with _conn() as con:
        row = con.execute(
            "SELECT direction, entry FROM trades WHERE id=?", (trade_id,)
        ).fetchone()
        if not row:
            return
        direction, entry = row["direction"], row["entry"]
        pnl = (exit_price - entry) if direction == "LONG" else (entry - exit_price)
        con.execute(
            "UPDATE trades SET result=?, exit_price=?, pnl=?, closed_at=? WHERE id=?",
            (result, exit_price, round(pnl, 2), ts, trade_id),
        )


def get_open_trades() -> list:
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM trades WHERE result='OPEN' ORDER BY id DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def get_recent_trades(limit: int = 20) -> list:
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM trades ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_stats() -> dict:
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM trades WHERE result != 'OPEN' ORDER BY id ASC"
        ).fetchall()
        closed = [dict(r) for r in rows]

    if not closed:
        return {
            "total_pnl": 0.0, "trade_count": 0, "win_count": 0,
            "loss_count": 0, "win_rate": 0.0, "avg_pnl": 0.0,
            "sharpe": None, "max_dd": 0.0, "equity_curve": [],
            "equity_timestamps": [],
        }

    pnl_list = [t["pnl"] for t in closed if t["pnl"] is not None]
    wins     = [p for p in pnl_list if p > 0]
    losses   = [p for p in pnl_list if p <= 0]

    cumulative, total = [], 0.0
    for p in pnl_list:
        total += p
        cumulative.append(round(total, 2))

    peak, max_dd = 0.0, 0.0
    for v in cumulative:
        if v > peak:
            peak = v
        dd = peak - v
        if dd > max_dd:
            max_dd = dd

    sharpe = None
    if len(pnl_list) >= 3:
        std_r = statistics.stdev(pnl_list)
        if std_r > 0:
            sharpe = round(statistics.mean(pnl_list) / std_r, 2)

    timestamps = [t["closed_at"][:16] if t["closed_at"] else "" for t in closed]

    return {
        "total_pnl"  : round(sum(pnl_list), 2),
        "trade_count": len(pnl_list),
        "win_count"  : len(wins),
        "loss_count" : len(losses),
        "win_rate"   : round(len(wins) / len(pnl_list) * 100, 1) if pnl_list else 0.0,
        "avg_pnl"    : round(sum(pnl_list) / len(pnl_list), 2) if pnl_list else 0.0,
        "sharpe"     : sharpe,
        "max_dd"     : round(max_dd, 2),
        "equity_curve"      : cumulative,
        "equity_timestamps" : timestamps,
    }


def auto_close_on_price(current_price: float):
    for trade in get_open_trades():
        direction = trade["direction"]
        target    = trade["target"]
        stop_val  = trade["stop"]
        trade_id  = trade["id"]

        if direction == "LONG":
            if current_price >= target:
                close_trade(trade_id, target, "WIN")
            elif current_price <= stop_val:
                close_trade(trade_id, stop_val, "LOSS")
        else:
            if current_price <= target:
                close_trade(trade_id, target, "WIN")
            elif current_price >= stop_val:
                close_trade(trade_id, stop_val, "LOSS")


def maybe_log_signal(signal: dict, current_price: float) -> bool:
    if not signal or not signal.get("direction"):
        return False

    open_trades = get_open_trades()

    if open_trades:
        latest = open_trades[0]
        if (latest["direction"] == signal["direction"] and
                abs(latest["entry"] - signal["entry"]) < 0.10):
            return False
        result = "WIN" if (
            (latest["direction"] == "LONG" and current_price > latest["entry"]) or
            (latest["direction"] == "SHORT" and current_price < latest["entry"])
        ) else "LOSS"
        close_trade(latest["id"], current_price, result)

    log_trade(signal)
    return True
