import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.ingestion.news_fetcher import fetch_all_news, filter_by_ticker  # noqa: E402
from src.ingestion.social_fetcher import fetch_all_social  # noqa: E402
from src.nlp.sentiment import FinBERTAnalyzer, analyze_dataframe  # noqa: E402
from src.nlp.aggregator import aggregate_sentiment  # noqa: E402

TICKER = "AAPL"
COMPANY = "Apple"

print("=" * 50)
print(f"Running sentiment pipeline for {TICKER}")
print("=" * 50)

print("\nFetching news...")
news_df = fetch_all_news()
news_df = filter_by_ticker(news_df, TICKER, company_name=COMPANY)

print("Fetching social data...")
social_df = fetch_all_social(TICKER)

all_df = pd.concat([news_df, social_df], ignore_index=True)
print(f"\nTotal texts to analyze: {len(all_df)}")

analyzer = FinBERTAnalyzer()
scored_df = analyze_dataframe(all_df, analyzer)

print("\n--- Sample Sentiment Results ---")
print(scored_df[["source", "title", "sentiment", "confidence"]].head(10).to_string())

print("\n--- Aggregated Signal ---")
report = aggregate_sentiment(scored_df, TICKER)
for key, value in report.items():
    print(f"{key}: {value}")

stocktwits = scored_df[scored_df["source"] == "stocktwits"].copy()
stocktwits = stocktwits[stocktwits["sentiment_label"].notna()]

if not stocktwits.empty:
    print(f"\n--- Stocktwits Validation ---")
    print(f"Posts with user labels: {len(stocktwits)}")

    stocktwits["st_label"] = stocktwits["sentiment_label"].map(
        {"Bullish": "positive", "Bearish": "negative"}
    )

    matches = (stocktwits["sentiment"] == stocktwits["st_label"]).sum()
    accuracy = round(matches / len(stocktwits) * 100, 1)
    print(f"FinBERT agreement with user labels: {accuracy}%")
