from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "signals.db"


def get_connection(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS signal_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            company TEXT NOT NULL,
            signal TEXT NOT NULL,
            score REAL NOT NULL,
            price_at_signal REAL,
            date_detected TEXT NOT NULL,
            is_complete INTEGER NOT NULL DEFAULT 0,
            date_completed TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS price_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            signal_id INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            date TEXT NOT NULL,
            price REAL NOT NULL,
            days_since_signal INTEGER NOT NULL,
            pct_change REAL NOT NULL,
            FOREIGN KEY (signal_id) REFERENCES signal_alerts(id)
        )
        """
    )

    cur.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_price_tracking_unique
        ON price_tracking(signal_id, date)
        """
    )

    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_signal_alerts_active
        ON signal_alerts(is_complete, date_detected)
        """
    )

    cur.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_signal_alerts_unique
        ON signal_alerts(ticker, signal, date_detected)
        """
    )

    conn.commit()


def insert_signal_alert(
    conn: sqlite3.Connection,
    ticker: str,
    company: str,
    signal: str,
    score: float,
    price_at_signal: float | None,
    date_detected: str,
) -> int:
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR IGNORE INTO signal_alerts (
            ticker, company, signal, score, price_at_signal, date_detected
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (ticker, company, signal, float(score), price_at_signal, date_detected),
    )
    conn.commit()

    if cur.lastrowid:
        return int(cur.lastrowid)

    cur.execute(
        """
        SELECT id
        FROM signal_alerts
        WHERE ticker = ? AND signal = ? AND date_detected = ?
        """,
        (ticker, signal, date_detected),
    )
    row = cur.fetchone()
    return int(row["id"]) if row else 0


def get_active_signals(
    conn: sqlite3.Connection,
    max_age_days: int = 14,
) -> list[sqlite3.Row]:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT *
        FROM signal_alerts
        WHERE is_complete = 0
          AND date(date_detected) >= date('now', ?)
        ORDER BY date_detected DESC
        """,
        (f"-{int(max_age_days)} days",),
    )
    return list(cur.fetchall())


def mark_signal_complete(conn: sqlite3.Connection, signal_id: int, date_completed: str) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE signal_alerts
        SET is_complete = 1,
            date_completed = ?
        WHERE id = ?
        """,
        (date_completed, int(signal_id)),
    )
    conn.commit()


def insert_price_tracking(
    conn: sqlite3.Connection,
    signal_id: int,
    ticker: str,
    date: str,
    price: float,
    days_since_signal: int,
    pct_change: float,
) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR IGNORE INTO price_tracking (
            signal_id, ticker, date, price, days_since_signal, pct_change
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            int(signal_id),
            ticker,
            date,
            float(price),
            int(days_since_signal),
            float(pct_change),
        ),
    )
    conn.commit()


def get_latest_tracking_rows(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT sa.id AS signal_id,
               sa.ticker,
               sa.company,
               sa.signal,
               sa.score,
               sa.price_at_signal,
               sa.date_detected,
               pt.date AS last_date,
               pt.price AS last_price,
               pt.days_since_signal,
               pt.pct_change
        FROM signal_alerts sa
        LEFT JOIN price_tracking pt
          ON pt.signal_id = sa.id
        WHERE pt.id IS NULL
           OR pt.id = (
                SELECT pt2.id
                FROM price_tracking pt2
                WHERE pt2.signal_id = sa.id
                ORDER BY date(pt2.date) DESC, pt2.id DESC
                LIMIT 1
           )
        ORDER BY date(sa.date_detected) DESC, sa.id DESC
        """
    )
    return list(cur.fetchall())


def get_active_signals_grouped(max_age_days: int = 14) -> list[dict]:
    """
    Returns one row per ticker: earliest active signal date, latest price update,
    and max favorable move seen so far.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        WITH active AS (
            SELECT *
            FROM signal_alerts
            WHERE is_complete = 0
              AND date(date_detected) >= date('now', ?)
        ),
        earliest_date AS (
            SELECT ticker, MIN(date_detected) AS min_date
            FROM active
            GROUP BY ticker
        ),
        earliest AS (
            SELECT a.*
            FROM active a
            JOIN earliest_date ed
              ON ed.ticker = a.ticker AND ed.min_date = a.date_detected
            JOIN (
                SELECT ticker, date_detected, MIN(id) AS min_id
                FROM active
                GROUP BY ticker, date_detected
            ) mi
              ON mi.ticker = a.ticker AND mi.date_detected = a.date_detected AND mi.min_id = a.id
        ),
        latest_pt AS (
            SELECT pt1.*
            FROM price_tracking pt1
            JOIN (
                SELECT signal_id, MAX(date(date)) AS max_date
                FROM price_tracking
                GROUP BY signal_id
            ) mx
              ON mx.signal_id = pt1.signal_id AND date(pt1.date) = mx.max_date
        )
        SELECT
            e.ticker,
            e.company,
            e.signal,
            e.id,
            e.date_detected AS date_detected,
            e.price_at_signal,
            lp.price AS current_price,
            lp.pct_change,
            lp.days_since_signal,
            (
                SELECT MAX(
                    CASE
                        WHEN e.signal = 'BULLISH' THEN pt2.pct_change
                        WHEN e.signal = 'BEARISH' THEN -pt2.pct_change
                        ELSE NULL
                    END
                )
                FROM price_tracking pt2
                WHERE pt2.signal_id = e.id
            ) AS max_move,
            (
                CASE
                    WHEN e.signal = 'BEARISH' THEN -COALESCE(lp.pct_change, 0)
                    ELSE COALESCE(lp.pct_change, 0)
                END
            ) AS favorable_move
        FROM earliest e
        LEFT JOIN latest_pt lp
          ON lp.signal_id = e.id
        ORDER BY e.signal, favorable_move DESC
        """,
        (f"-{int(max_age_days)} days",),
    )

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_completed_signals_grouped() -> list[dict]:
    """
    Returns one row per ticker+signal+date_detected for completed signals,
    with final price, final return, and max favorable move during the tracking window.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        WITH completed AS (
            SELECT *
            FROM signal_alerts
            WHERE is_complete = 1
        ),
        latest_pt AS (
            SELECT pt1.*
            FROM price_tracking pt1
            JOIN (
                SELECT signal_id, MAX(date(date)) AS max_date
                FROM price_tracking
                GROUP BY signal_id
            ) mx
              ON mx.signal_id = pt1.signal_id AND date(pt1.date) = mx.max_date
        )
        SELECT
            sa.ticker,
            sa.company,
            sa.signal,
            sa.id,
            sa.date_detected,
            sa.price_at_signal,
            lp.price AS final_price,
            lp.pct_change AS final_pct,
            (
                SELECT MAX(
                    CASE
                        WHEN sa.signal = 'BULLISH' THEN pt2.pct_change
                        WHEN sa.signal = 'BEARISH' THEN -pt2.pct_change
                        ELSE NULL
                    END
                )
                FROM price_tracking pt2
                WHERE pt2.signal_id = sa.id
            ) AS max_move
        FROM completed sa
        LEFT JOIN latest_pt lp
          ON lp.signal_id = sa.id
        ORDER BY date(sa.date_detected) DESC, sa.id DESC
        """
    )

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
