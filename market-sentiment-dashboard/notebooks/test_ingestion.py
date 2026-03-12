import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.ingestion.news_fetcher import fetch_all_news, filter_by_ticker  # noqa: E402
from src.ingestion.price_fetcher import fetch_price_history, fetch_ticker_info  # noqa: E402
from src.ingestion.social_fetcher import fetch_all_social  # noqa: E402

TICKER = "AAPL"

print("=" * 50)
print("Testing News Ingestion")
print("=" * 50)
news_df = fetch_all_news()
if not news_df.empty:
    print(news_df[["source", "title"]].head(5))

aapl_news = filter_by_ticker(news_df, TICKER, company_name="Apple")
print(f"\nArticles mentioning {TICKER}: {len(aapl_news)}")
if not aapl_news.empty:
    print(aapl_news[["source", "title"]].head(3))

print("\n" + "=" * 50)
print("Testing Social Ingestion")
print("=" * 50)
social_df = fetch_all_social(TICKER)
if not social_df.empty:
    print(social_df[["source", "title", "sentiment_label"]].head(5))

print("\n" + "=" * 50)
print("Testing Price Data")
print("=" * 50)
prices = fetch_price_history(TICKER)
if not prices.empty:
    print(prices.tail(5))

info = fetch_ticker_info(TICKER)
print(f"\nCompany: {info.get('company_name')}")
print(f"Sector: {info.get('sector')}")
