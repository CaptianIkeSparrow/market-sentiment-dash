import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.ingestion.news_fetcher import fetch_all_news, filter_by_ticker  # noqa: E402
from src.ingestion.social_fetcher import fetch_all_social  # noqa: E402
from src.nlp.sentiment import FinBERTAnalyzer, analyze_dataframe  # noqa: E402
from src.nlp.aggregator import aggregate_sentiment  # noqa: E402
from src.anomaly.detector import (  # noqa: E402
    detect_sentiment_anomaly,
    detect_volume_anomaly,
    generate_alert,
)
from src.anomaly.history import (  # noqa: E402
    simulate_historical_scores,
    simulate_historical_counts,
    build_history_dataframe,
)

TICKER = "AAPL"
COMPANY = "Apple"

print("=" * 50)
print(f"Full pipeline test: {TICKER}")
print("=" * 50)

news_df = fetch_all_news()
news_df = filter_by_ticker(news_df, TICKER, company_name=COMPANY)
social_df = fetch_all_social(TICKER)
all_df = pd.concat([news_df, social_df], ignore_index=True)

analyzer = FinBERTAnalyzer()
scored_df = analyze_dataframe(all_df, analyzer)
report = aggregate_sentiment(scored_df, TICKER)

current_score = report["overall_score"]
current_count = report["total_articles"]

print(f"\nCurrent sentiment score: {current_score}")
print(f"Current article count: {current_count}")

historical_scores = simulate_historical_scores(days=30)
historical_counts = simulate_historical_counts(days=30)

print(
    f"\nHistorical sentiment mean: {sum(historical_scores)/len(historical_scores):.4f}"
)
print(f"Historical article count mean: {sum(historical_counts)/len(historical_counts):.0f}")

print("\n--- Anomaly Detection Results ---")
sentiment_anomaly = detect_sentiment_anomaly(historical_scores, current_score)
volume_anomaly = detect_volume_anomaly(historical_counts, current_count)

print(f"\nSentiment Anomaly:")
print(f"  Is anomaly: {sentiment_anomaly.is_anomaly}")
print(f"  Severity: {sentiment_anomaly.severity}")
print(f"  Z-score: {sentiment_anomaly.z_score}")
print(f"  Description: {sentiment_anomaly.description}")

print(f"\nVolume Anomaly:")
print(f"  Is anomaly: {volume_anomaly.is_anomaly}")
print(f"  Severity: {volume_anomaly.severity}")
print(f"  Z-score: {volume_anomaly.z_score}")
print(f"  Description: {volume_anomaly.description}")

print("\n--- Alert ---")
alert = generate_alert(TICKER, sentiment_anomaly, volume_anomaly, current_score)
if alert:
    print(f"Ticker: {alert['ticker']}")
    print(f"Level: {alert['alert_level']}")
    print(f"Score: {alert['current_sentiment_score']}")
    for a in alert["alerts"]:
        print(f"  - {a}")
    print(f"Action: {alert['action']}")
else:
    print("✅ No anomalies detected — sentiment is within normal range")

print("\n--- Historical Context (last 7 days) ---")
history_df = build_history_dataframe(TICKER, days=7)
print(history_df[["date", "sentiment_score", "article_count"]].to_string(index=False))
