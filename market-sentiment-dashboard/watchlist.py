#!/usr/bin/env python3
"""
Watchlist Scanner
-----------------
Scans all tickers in your watchlist and ranks them
from most bearish to most bullish.

No LLM calls — pure signal ranking.
For a full LLM briefing on a specific ticker run:
    python app.py TICKER

Usage:
    python watchlist.py
"""

import os
import sys

import pandas as pd
from dotenv import load_dotenv
from loguru import logger

load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"

logger.remove()


def action_from_score(score: float) -> str:
    """
    Convert a sentiment score into a simple action label.
    """
    if score > 0.15:
        return "BUY"
    if score < -0.15:
        return "SELL"
    return "HOLD"


def analyze_ticker(
    ticker: str,
    company_name: str,
    analyzer,
) -> dict | None:
    """
    Run the sentiment pipeline for a single ticker.
    Returns a summary dict or None if data fetch fails.
    """
    from src.ingestion.news_fetcher import fetch_all_news, filter_by_ticker
    from src.ingestion.social_fetcher import fetch_all_social
    from src.nlp.sentiment import analyze_dataframe
    from src.nlp.aggregator import aggregate_sentiment
    from src.anomaly.detector import detect_sentiment_anomaly, detect_volume_anomaly
    from src.anomaly.history import simulate_historical_scores, simulate_historical_counts

    try:
        news_df = fetch_all_news()
        news_df = filter_by_ticker(news_df, ticker, company_name=company_name)
        social_df = fetch_all_social(ticker)
        all_df = pd.concat([news_df, social_df], ignore_index=True)

        if all_df.empty:
            return None

        scored_df = analyze_dataframe(all_df, analyzer)
        report = aggregate_sentiment(scored_df, ticker)

        historical_scores = simulate_historical_scores(days=30)
        historical_counts = simulate_historical_counts(days=30)
        sentiment_anomaly = detect_sentiment_anomaly(
            historical_scores, report["overall_score"]
        )
        volume_anomaly = detect_volume_anomaly(historical_counts, report["total_articles"])

        severities = ["none", "mild", "moderate", "severe"]
        worst = max(
            sentiment_anomaly.severity,
            volume_anomaly.severity,
            key=lambda s: severities.index(s),
        )

        anomaly_display = {"none": "", "mild": "MILD", "moderate": "MODERATE", "severe": "SEVERE"}[
            worst
        ]

        return {
            "ticker": ticker,
            "company": company_name,
            "score": report["overall_score"],
            "signal": report["signal"],
            "positive_pct": report["positive_pct"],
            "negative_pct": report["negative_pct"],
            "neutral_pct": report["neutral_pct"],
            "velocity": report["sentiment_velocity"],
            "total_articles": report["total_articles"],
            "anomaly": anomaly_display,
            "anomaly_severity": worst,
        }

    except Exception as e:
        print(f"  - Failed to analyze {ticker}: {e}")
        return None


def print_rankings(results: list[dict]):
    """Print a clean ranked table of sentiment signals."""

    divider = "=" * 75

    print(f"\n{divider}")
    print("  WATCHLIST SENTIMENT RANKINGS")
    print(f"{divider}")
    print(f"  {'RANK':<5} {'TICKER':<7} {'COMPANY':<22} {'SCORE':<8} {'SIGNAL':<12} {'ANOMALY'}")
    print("-" * 75)

    signal_display = {
        "bullish": "BULLISH",
        "bearish": "BEARISH",
        "neutral": "NEUTRAL",
    }

    for i, r in enumerate(results, 1):
        signal = signal_display.get(r["signal"], r["signal"])
        score = f"{r['score']:+.4f}"
        print(
            f"  {i:<5} {r['ticker']:<7} {r['company']:<22} "
            f"{score:<8} {signal:<12} {r['anomaly']}"
        )

    print(f"{divider}")

    print("\n  Score legend:")
    print("  - Range: -1.0 (very bearish) to +1.0 (very bullish)")
    print("  - Neutral band: -0.15 to +0.15 (roughly 'hold')")

    bullish = sum(1 for r in results if r["signal"] == "bullish")
    bearish = sum(1 for r in results if r["signal"] == "bearish")
    neutral = len(results) - bullish - bearish
    anomalies = sum(1 for r in results if r["anomaly_severity"] in ["moderate", "severe"])

    print(f"\n  Market Breadth: {bullish} bullish  {neutral} neutral  {bearish} bearish")
    if anomalies:
        print(f"  {anomalies} ticker(s) showing anomalous activity")

    print("\n  Tip: run 'python app.py TICKER' for a full LLM briefing on any ticker")
    print(f"{divider}\n")


def print_detail_table(results: list[dict]):
    """Print detailed breakdown table below rankings."""

    print("  DETAILED BREAKDOWN")
    print("-" * 75)
    print(
        f"  {'TICKER':<7} {'POS%':<8} {'NEG%':<8} {'NEU%':<8} "
        f"{'VELOCITY':<12} {'ARTICLES':<9} {'ACTION'}"
    )
    print("-" * 75)

    for r in results:
        velocity_str = f"{r['velocity']:+.4f}"
        velocity_dir = "UP" if r["velocity"] > 0 else "DOWN"
        action = action_from_score(float(r["score"]))
        print(
            f"  {r['ticker']:<7} {r['positive_pct']:<8} {r['negative_pct']:<8} "
            f"{r['neutral_pct']:<8} {velocity_str} {velocity_dir:<4} "
            f"{r['total_articles']:<9} {action}"
        )

    print("-" * 75)
    print("  Velocity: UP = sentiment improving, DOWN = deteriorating\n")


def main():
    from src.config.tickers import get_watchlist
    from src.nlp.sentiment import FinBERTAnalyzer

    watchlist = get_watchlist()

    print(f"\nScanning {len(watchlist)} tickers...")
    print("Loading FinBERT model...")

    analyzer = FinBERTAnalyzer()
    print("✅ Model loaded\n")

    results: list[dict] = []
    for i, (ticker, company) in enumerate(watchlist, 1):
        print(f"  [{i}/{len(watchlist)}] Analyzing {ticker}...", end=" ", flush=True)
        result = analyze_ticker(ticker, company, analyzer)
        if result:
            results.append(result)
            print(f"{result['score']:+.4f}")
        else:
            print("skipped")

    if not results:
        print("No results. Check your internet connection and try again.")
        sys.exit(1)

    results.sort(key=lambda x: x["score"])

    print_rankings(results)
    print_detail_table(results)


if __name__ == "__main__":
    main()
