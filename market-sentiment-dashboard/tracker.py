#!/usr/bin/env python3
"""
Signal Performance Tracker
--------------------------
Shows how recent bullish/bearish signals are performing over time.
Reads from SQLite and displays the latest outcome per signal.

Usage:
    python tracker.py
    python tracker.py --all
"""

from __future__ import annotations

import sys

from src.database.db import (
    get_connection,
    get_active_signals_grouped,
    get_completed_signals_grouped,
    init_db,
)


def get_trend(signal_id: int, signal: str) -> str:
    """
    Compare last two price updates to get a simple trend indicator.
    Uses favorable move for bearish signals (i.e. -pct_change).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT pct_change
        FROM price_tracking
        WHERE signal_id = ?
        ORDER BY date(date) DESC, id DESC
        LIMIT 2
        """,
        (int(signal_id),),
    )
    rows = cur.fetchall()
    conn.close()

    if len(rows) < 2:
        return "-"

    latest = float(rows[0]["pct_change"] or 0.0)
    prev = float(rows[1]["pct_change"] or 0.0)

    if str(signal).upper() == "BEARISH":
        latest = -latest
        prev = -prev

    diff = latest - prev
    if diff > 0.3:
        return "^"
    if diff < -0.3:
        return "v"
    return "-"


def _format_pct(pct: float | None) -> str:
    if pct is None:
        return "n/a"
    return f"{float(pct):+.1f}%"


def _print_table(title: str, rows: list[dict]) -> None:
    divider = "=" * 105
    print(f"\n{divider}")
    print(f"  {title}")
    print(f"{divider}")

    header = (
        f"  {'TICKER':<8} {'SIGNAL':<10} {'DETECTED':<13} {'ENTRY $':<10} "
        f"{'NOW $':<10} {'CHANGE':<12} {'MAX':<10} {'TREND':<8} {'DAYS'}"
    )
    print(header)
    print("-" * 105)

    for s in rows:
        signal_id = int(s["id"])
        trend = get_trend(signal_id, str(s["signal"]))
        ticker = str(s["ticker"])
        signal = str(s["signal"]).upper()
        detected = str(s["date_detected"])[:10]

        entry_val = s.get("price_at_signal")
        now_val = s.get("current_price")
        change_val = s.get("pct_change")
        max_move_val = s.get("max_move")
        days = int(s.get("days_since_signal") or 0)

        entry = f"${float(entry_val):.2f}" if entry_val is not None else "n/a"
        now_price = f"${float(now_val):.2f}" if now_val is not None else "pending"
        change = _format_pct(change_val)
        max_move = _format_pct(max_move_val)

        print(
            f"  {ticker:<8} {signal:<10} {detected:<13} {entry:<10} {now_price:<10} "
            f"{change:<12} {max_move:<10} {trend:<8} {days}d"
        )

def _outcome(signal: str, final_pct: float | None) -> str:
    """
    Classify a completed signal into HIT/WEAK/MISS.
    Uses a +/-2.0% threshold for HIT, and +/-2.0% band for WEAK.
    """
    if final_pct is None:
        return "PENDING"

    pct = float(final_pct)
    sig = str(signal).upper()

    if abs(pct) <= 2.0:
        return "WEAK"

    if sig == "BULLISH":
        return "HIT" if pct > 2.0 else "MISS"
    if sig == "BEARISH":
        return "HIT" if pct < -2.0 else "MISS"
    return "N/A"


def show_active() -> int:
    conn = get_connection()
    init_db(conn)
    conn.close()

    signals = get_active_signals_grouped(max_age_days=14)
    if not signals:
        print("No active signals found yet. Run watchlist.py first.")
        return 0

    bullish = [s for s in signals if str(s["signal"]).upper() == "BULLISH"]
    bearish = [s for s in signals if str(s["signal"]).upper() == "BEARISH"]
    other = [
        s
        for s in signals
        if str(s["signal"]).upper() not in ["BULLISH", "BEARISH"]
    ]

    _print_table("BULLISH SIGNALS (ACTIVE)", bullish)
    _print_table("BEARISH SIGNALS (ACTIVE)", bearish)
    if other:
        _print_table("OTHER SIGNALS (ACTIVE)", other)

    return 0


def show_all() -> int:
    conn = get_connection()
    init_db(conn)
    conn.close()

    completed = get_completed_signals_grouped()
    if not completed:
        print("No completed signals yet.")
        return 0

    divider = "=" * 110
    print(f"\n{divider}")
    print("  COMPLETED SIGNALS")
    print(f"{divider}")

    header = (
        f"  {'TICKER':<8} {'SIGNAL':<10} {'DETECTED':<13} {'ENTRY $':<10} "
        f"{'FINAL $':<10} {'CHANGE':<12} {'MAX':<10} {'OUTCOME'}"
    )
    print(header)
    print("-" * 110)

    for s in completed:
        ticker = str(s["ticker"])
        signal = str(s["signal"]).upper()
        detected = str(s["date_detected"])[:10]

        entry_val = s.get("price_at_signal")
        final_val = s.get("final_price")
        final_pct = s.get("final_pct")
        max_move_val = s.get("max_move")

        entry = f"${float(entry_val):.2f}" if entry_val is not None else "n/a"
        final_price = f"${float(final_val):.2f}" if final_val is not None else "n/a"
        change = _format_pct(final_pct)
        max_move = _format_pct(max_move_val)
        outcome = _outcome(signal, final_pct)

        print(
            f"  {ticker:<8} {signal:<10} {detected:<13} {entry:<10} {final_price:<10} "
            f"{change:<12} {max_move:<10} {outcome}"
        )

    return 0


def main() -> int:
    if "--all" in sys.argv:
        return show_all()
    return show_active()


if __name__ == "__main__":
    raise SystemExit(main())
