import feedparser
import pandas as pd
from datetime import datetime, timezone
from loguru import logger
import requests


RSS_FEEDS = {
    "cnbc": "https://www.cnbc.com/id/10001147/device/rss/rss.html",
    "marketwatch": "https://feeds.content.dowjones.io/public/rss/mw_realtimeheadlines",
    "yahoo_finance": "https://finance.yahoo.com/news/rssindex",
    "benzinga": "https://www.benzinga.com/feed",
    "investor_place": "https://investorplace.com/feed/",
    "motley_fool": "https://www.fool.com/feeds/index.aspx",
}


def fetch_feed(source_name: str, url: str) -> list[dict]:
    """Fetch and parse a single RSS feed."""
    try:
        resp = requests.get(
            url,
            headers={
                "User-Agent": "market-sentiment-dashboard/1.0 (+https://example.com)"
            },
            timeout=20,
        )
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
        articles = []

        if getattr(feed, "bozo", 0):
            exc = getattr(feed, "bozo_exception", None)
            logger.warning(f"⚠️ {source_name}: feed parse bozo={feed.bozo} exc={exc}")

        for entry in feed.entries:
            articles.append(
                {
                    "source": source_name,
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", ""),
                    "url": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }
            )

        logger.info(f"✅ {source_name}: {len(articles)} articles fetched")
        return articles

    except Exception as e:
        logger.error(f"Failed to fetch {source_name}: {e}")
        return []


def fetch_all_news() -> pd.DataFrame:
    """Fetch articles from all RSS feeds and return as a DataFrame."""
    all_articles = []

    for source_name, url in RSS_FEEDS.items():
        articles = fetch_feed(source_name, url)
        all_articles.extend(articles)

    df = pd.DataFrame(all_articles)

    if df.empty:
        logger.warning("No articles fetched from any source")
        return df

    df = df.drop_duplicates(subset=["url"])
    df = df.sort_values("fetched_at", ascending=False).reset_index(drop=True)

    logger.info(f"Total articles fetched: {len(df)}")
    return df


def filter_by_ticker(df: pd.DataFrame, ticker: str, company_name: str = "") -> pd.DataFrame:
    """Filter articles that mention a specific ticker or company."""
    if df.empty:
        return df

    mask = df["title"].str.contains(ticker, case=False, na=False, regex=False) | df[
        "summary"
    ].str.contains(ticker, case=False, na=False, regex=False)

    if company_name:
        mask = mask | (
            df["title"].str.contains(company_name, case=False, na=False, regex=False)
            | df["summary"].str.contains(company_name, case=False, na=False, regex=False)
        )

    filtered = df[mask].reset_index(drop=True)
    logger.info(f"Articles mentioning {ticker}: {len(filtered)}")
    return filtered
