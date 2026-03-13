#!/usr/bin/env python3
"""
Tracker Updater
---------------
Runs daily (ideally at/after market close) to record price performance
for recently-detected signals.

Flow:
- Load active signals (not complete, < 14 days old)
- Fetch current price for each ticker
- Write a new price_tracking row with pct change from entry price
- Mark signals complete after 14 days
"""

from __future__ import annotations

from datetime import datetime

from src.database.db import (
    get_connection,
    get_active_signals,
    init_db,
    insert_price_tracking,
    mark_signal_complete,
)
from src.ingestion.price_fetcher import fetch_price_history


def _days_since(date_detected: str, today: datetime) -> int:
    detected = datetime.fromisoformat(date_detected)
    return max(0, (today.date() - detected.date()).days)


def main() -> int:
    conn = get_connection()
    init_db(conn)

    today = datetime.now()
    today_str = today.date().isoformat()

    signals = get_active_signals(conn, max_age_days=14)
    if not signals:
        conn.close()
        return 0

    for s in signals:
        signal_id = int(s["id"])
        ticker = str(s["ticker"])
        entry = s["price_at_signal"]

        if entry is None:
            continue

        days = _days_since(str(s["date_detected"]), today)

        price_df = fetch_price_history(ticker, period="1mo")
        if price_df.empty:
            continue

        now_price = float(price_df["Close"].iloc[-1])
        pct_change = ((now_price - float(entry)) / float(entry)) * 100 if float(entry) else 0.0

        insert_price_tracking(
            conn=conn,
            signal_id=signal_id,
            ticker=ticker,
            date=today_str,
            price=now_price,
            days_since_signal=days,
            pct_change=pct_change,
        )

        if days >= 14:
            mark_signal_complete(conn, signal_id=signal_id, date_completed=today_str)

    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

