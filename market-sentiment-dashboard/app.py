#!/usr/bin/env python3
"""
Market Sentiment Dashboard
--------------------------
Usage: python app.py <TICKER> [COMPANY_NAME]

Examples:
    python app.py NVDA
    python app.py AAPL Apple
    python app.py TSLA Tesla
    python app.py --list
"""

import os
import sys

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

os.environ["TOKENIZERS_PARALLELISM"] = "false"


def run_pipeline(ticker: str, company_name: str):
    """Run the full sentiment analysis pipeline for a ticker."""

    print(f"\nStarting Market Sentiment Analysis for {ticker}...")
    print("=" * 60)

    print("\nFetching data...")

    from src.ingestion.news_fetcher import fetch_all_news, filter_by_ticker
    from src.ingestion.social_fetcher import fetch_all_social
    from src.ingestion.price_fetcher import fetch_price_history, fetch_ticker_info

    news_df = fetch_all_news()
    news_df = filter_by_ticker(news_df, ticker, company_name=company_name)
    social_df = fetch_all_social(ticker)
    all_df = pd.concat([news_df, social_df], ignore_index=True)
    price_data = fetch_price_history(ticker, period="1mo")
    ticker_info = fetch_ticker_info(ticker)

    if company_name == ticker and ticker_info.get("company_name"):
        company_name = ticker_info["company_name"]

    total = len(all_df)
    print(f"✅ {total} total signals collected")
    print(f"   • {len(news_df)} news articles")
    print(f"   • {len(social_df)} social signals")

    if all_df.empty:
        print("No data found. Try a different ticker.")
        sys.exit(1)

    print("\nRunning sentiment analysis...")

    from src.nlp.sentiment import FinBERTAnalyzer, analyze_dataframe
    from src.nlp.aggregator import aggregate_sentiment

    analyzer = FinBERTAnalyzer()
    scored_df = analyze_dataframe(all_df, analyzer)
    report = aggregate_sentiment(scored_df, ticker)

    print(
        f"✅ Sentiment: {report['signal'].upper()} (score: {report['overall_score']})"
    )
    print(f"   • Positive: {report['positive_pct']}%")
    print(f"   • Negative: {report['negative_pct']}%")
    print(f"   • Neutral:  {report['neutral_pct']}%")

    print("\nRunning anomaly detection...")

    from src.anomaly.detector import (
        detect_sentiment_anomaly,
        detect_volume_anomaly,
        generate_alert,
    )
    from src.anomaly.history import (
        simulate_historical_scores,
        simulate_historical_counts,
    )

    historical_scores = simulate_historical_scores(days=30)
    historical_counts = simulate_historical_counts(days=30)
    sentiment_anomaly = detect_sentiment_anomaly(historical_scores, report["overall_score"])
    volume_anomaly = detect_volume_anomaly(historical_counts, report["total_articles"])

    alert = generate_alert(ticker, sentiment_anomaly, volume_anomaly, report["overall_score"])

    if alert:
        print(f"✅ Anomaly detected: {alert['alert_level']}")
        for a in alert["alerts"]:
            print(f"   - {a}")
    else:
        print("✅ No anomalies detected — sentiment within normal range")

    print("\nGenerating analyst briefing...")

    from src.llm.briefing import generate_briefing, print_briefing

    briefing = generate_briefing(
        ticker=ticker,
        company_name=company_name,
        sentiment_report=report,
        sentiment_anomaly=sentiment_anomaly,
        volume_anomaly=volume_anomaly,
        price_data=price_data,
        scored_df=scored_df,
    )

    print_briefing(briefing)

    if not price_data.empty:
        latest = float(price_data["Close"].iloc[-1])
        prev = float(price_data["Close"].iloc[-2]) if len(price_data) > 1 else latest
        change = ((latest - prev) / prev) * 100 if prev else 0.0
        print(f"Latest Price: ${latest:.2f} ({change:+.2f}% today)\n")


def main():
    from src.config.tickers import get_company_name, list_supported_tickers

    if len(sys.argv) < 2:
        print(__doc__)
        print("Error: Please provide a ticker symbol.")
        print("Example: python app.py NVDA")
        print("\nRun 'python app.py --list' to see all supported tickers.")
        sys.exit(1)

    if sys.argv[1] == "--list":
        list_supported_tickers()
        sys.exit(0)

    ticker = sys.argv[1].upper().strip()

    if len(sys.argv) >= 3:
        company_name = sys.argv[2]
    else:
        company_name = get_company_name(ticker)

    run_pipeline(ticker, company_name)


if __name__ == "__main__":
    main()
