#!/usr/bin/env python3
"""
Signal Performance Tracker
--------------------------
Shows how recent bullish/bearish signals are performing over time.
Reads from SQLite and displays the latest outcome per signal.

Usage:
    python tracker.py
"""

from __future__ import annotations

from src.database.db import get_connection, get_latest_tracking_rows, init_db


def _print_table(title: str, rows) -> None:
    divider = "=" * 72
    print(f"\n{divider}")
    print(f"  {title}")
    print(f"{divider}")

    header = (
        f"{'TICKER':<7} {'DATE':<12} {'ENTRY':<10} {'NOW':<10} {'CHANGE':<9} {'DAYS'}"
    )
    print(header)
    print("-" * len(header))

    for r in rows:
        ticker = str(r["ticker"])
        date_detected = str(r["date_detected"])[:10]
        entry = r["price_at_signal"]
        now_price = r["last_price"] if r["last_price"] is not None else entry
        pct = r["pct_change"] if r["pct_change"] is not None else 0.0
        days = r["days_since_signal"] if r["days_since_signal"] is not None else 0

        entry_str = f"${float(entry):.2f}" if entry is not None else "n/a"
        now_str = f"${float(now_price):.2f}" if now_price is not None else "n/a"
        change_str = f"{float(pct):+.1f}%" if entry is not None else "n/a"

        print(
            f"{ticker:<7} {date_detected:<12} {entry_str:<10} "
            f"{now_str:<10} {change_str:<9} {days}"
        )


def main() -> int:
    conn = get_connection()
    init_db(conn)

    rows = get_latest_tracking_rows(conn)
    conn.close()

    if not rows:
        print("No signals found yet. Run watchlist.py first.")
        return 0

    bullish = [r for r in rows if str(r["signal"]).upper() == "BULLISH"]
    bearish = [r for r in rows if str(r["signal"]).upper() == "BEARISH"]
    other = [
        r
        for r in rows
        if str(r["signal"]).upper() not in ["BULLISH", "BEARISH"]
    ]

    _print_table("BULLISH SIGNALS", bullish)
    _print_table("BEARISH SIGNALS", bearish)
    if other:
        _print_table("OTHER SIGNALS", other)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
