import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.ingestion.news_fetcher import fetch_all_news, filter_by_ticker  # noqa: E402
from src.ingestion.social_fetcher import fetch_all_social  # noqa: E402
from src.ingestion.price_fetcher import fetch_price_history, fetch_ticker_info  # noqa: E402
from src.nlp.sentiment import FinBERTAnalyzer, analyze_dataframe  # noqa: E402
from src.nlp.aggregator import aggregate_sentiment  # noqa: E402
from src.anomaly.detector import (  # noqa: E402
    detect_sentiment_anomaly,
    detect_volume_anomaly,
    generate_alert,
)
from src.anomaly.history import simulate_historical_scores, simulate_historical_counts  # noqa: E402
from src.llm.briefing import generate_briefing, print_briefing  # noqa: E402

TICKER = "NVDA"
COMPANY = "Nvidia"

print(f"Running full pipeline for {TICKER}...\n")

news_df = fetch_all_news()
news_df = filter_by_ticker(news_df, TICKER, company_name=COMPANY)
social_df = fetch_all_social(TICKER)
all_df = pd.concat([news_df, social_df], ignore_index=True)
price_data = fetch_price_history(TICKER, period="1mo")
ticker_info = fetch_ticker_info(TICKER)

analyzer = FinBERTAnalyzer()
scored_df = analyze_dataframe(all_df, analyzer)
report = aggregate_sentiment(scored_df, TICKER)

historical_scores = simulate_historical_scores(days=30)
historical_counts = simulate_historical_counts(days=30)
sentiment_anomaly = detect_sentiment_anomaly(historical_scores, report["overall_score"])
volume_anomaly = detect_volume_anomaly(historical_counts, report["total_articles"])

alert = generate_alert(TICKER, sentiment_anomaly, volume_anomaly, report["overall_score"])
if alert:
    print(f"ALERT: {alert['alert_level']}")
    for a in alert["alerts"]:
        print(f"   - {a}")
    print()

briefing = generate_briefing(
    ticker=TICKER,
    company_name=COMPANY,
    sentiment_report=report,
    sentiment_anomaly=sentiment_anomaly,
    volume_anomaly=volume_anomaly,
    price_data=price_data,
    scored_df=scored_df,
)

print_briefing(briefing)
