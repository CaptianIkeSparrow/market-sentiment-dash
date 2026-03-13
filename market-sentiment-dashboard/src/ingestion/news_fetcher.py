"""
src/ingestion/news_fetcher.py

Fetches financial news from:
  1. General RSS feeds (broad market news)
  2. Yahoo Finance per-ticker RSS (ticker-specific articles) ← NEW
"""

import feedparser
import pandas as pd
import requests
from loguru import logger
from datetime import datetime

# ── General market RSS feeds ──────────────────────────────────────────────────
RSS_FEEDS = {
    "cnbc":           "https://www.cnbc.com/id/10001147/device/rss/rss.html",
    "marketwatch":    "https://feeds.content.dowjones.io/public/rss/mw_realtimeheadlines",
    "yahoo_finance":  "https://finance.yahoo.com/news/rssindex",
    "benzinga":       "https://www.benzinga.com/feed",
    "investor_place": "https://investorplace.com/feed/",
    "motley_fool":    "https://www.fool.com/feeds/index.aspx",
}

# ── Ticker alias map for broader RSS matching ─────────────────────────────────
TICKER_ALIASES = {
    "AAPL":  ["Apple", "iPhone", "Tim Cook", "App Store", "MacBook"],
    "MSFT":  ["Microsoft", "Satya Nadella", "Azure", "Windows", "Copilot"],
    "GOOGL": ["Google", "Alphabet", "Sundar Pichai", "YouTube", "Gemini"],
    "GOOG":  ["Google", "Alphabet", "Sundar Pichai", "YouTube", "Gemini"],
    "AMZN":  ["Amazon", "Andy Jassy", "AWS", "Prime"],
    "META":  ["Meta", "Facebook", "Mark Zuckerberg", "Instagram", "WhatsApp"],
    "NVDA":  ["Nvidia", "Jensen Huang", "GeForce", "CUDA", "H100"],
    "TSLA":  ["Tesla", "Elon Musk", "Cybertruck", "Powerwall"],
    "AMD":   ["AMD", "Lisa Su", "Ryzen", "Radeon"],
    "INTC":  ["Intel", "Pat Gelsinger"],
    "PLTR":  ["Palantir", "Alex Karp"],
    "COIN":  ["Coinbase", "Brian Armstrong"],
    "CRWD":  ["CrowdStrike", "George Kurtz"],
    "NFLX":  ["Netflix", "Ted Sarandos"],
    "JPM":   ["JPMorgan", "Jamie Dimon"],
    "BAC":   ["Bank of America"],
    "GS":    ["Goldman Sachs"],
    "MS":    ["Morgan Stanley"],
    "LMT":   ["Lockheed Martin"],
    "NOC":   ["Northrop Grumman"],
    "RTX":   ["Raytheon", "RTX"],
    "XOM":   ["ExxonMobil", "Exxon"],
    "CVX":   ["Chevron"],
    "MSTR":  ["MicroStrategy", "Michael Saylor"],
    "MARA":  ["Marathon Digital"],
    "RIOT":  ["Riot Platforms"],
}


def fetch_feed(name: str, url: str, timeout: int = 10) -> pd.DataFrame:
    """Fetch a single RSS feed and return as a DataFrame."""
    try:
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries:
            articles.append({
                "source":    name,
                "title":     entry.get("title", ""),
                "summary":   entry.get("summary", ""),
                "url":       entry.get("link", ""),
                "published": entry.get("published", ""),
            })
        df = pd.DataFrame(articles)
        logger.info(f"✅ {name}: {len(df)} articles fetched")
        return df
    except Exception as e:
        logger.error(f"❌ Failed to fetch {name}: {e}")
        return pd.DataFrame()


def fetch_all_news() -> pd.DataFrame:
    """Fetch all general RSS feeds and return combined DataFrame."""
    frames = []
    for name, url in RSS_FEEDS.items():
        df = fetch_feed(name, url)
        if not df.empty:
            frames.append(df)

    if not frames:
        logger.warning("No news articles fetched from any RSS feed")
        return pd.DataFrame()

    combined = pd.concat(frames, ignore_index=True)
    combined = combined.drop_duplicates(subset=["title"]).reset_index(drop=True)
    logger.info(f"📰 Total articles fetched: {len(combined)}")
    return combined


def fetch_yahoo_ticker_news(ticker: str) -> pd.DataFrame:
    """
    Fetch Yahoo Finance's per-ticker RSS feed.
    Returns articles specifically about this ticker.

    URL: https://finance.yahoo.com/rss/headline?s=TICKER
    Free, no auth, no rate limits in practice.
    """
    url = f"https://finance.yahoo.com/rss/headline?s={ticker.upper()}"
    source_name = f"yahoo_{ticker.lower()}"

    try:
        feed = feedparser.parse(url)

        if not feed.entries:
            logger.warning(f"  Yahoo ticker feed empty for {ticker}")
            return pd.DataFrame()

        articles = []
        for entry in feed.entries:
            articles.append({
                "source":    source_name,
                "title":     entry.get("title", ""),
                "summary":   entry.get("summary", ""),
                "url":       entry.get("link", ""),
                "published": entry.get("published", ""),
            })

        df = pd.DataFrame(articles)
        logger.info(f" Yahoo ticker feed ({ticker}): {len(df)} articles fetched")
        return df

    except Exception as e:
        logger.error(f"❌ Yahoo ticker feed failed for {ticker}: {e}")
        return pd.DataFrame()


def filter_by_ticker(
    df: pd.DataFrame,
    ticker: str,
    company_name: str = "",
) -> pd.DataFrame:
    """
    Filter general RSS articles that mention a specific ticker or company.
    Uses TICKER_ALIASES for broader matching.
    """
    if df.empty:
        return df

    # Build full list of search terms
    search_terms = [ticker.upper()]
    if company_name:
        search_terms.append(company_name)

    # Add aliases
    aliases = TICKER_ALIASES.get(ticker.upper(), [])
    search_terms.extend(aliases)

    # Build match mask across all terms
    mask = pd.Series([False] * len(df), index=df.index)
    for term in search_terms:
        mask = mask | (
            df["title"].str.contains(term, case=False, na=False) |
            df["summary"].str.contains(term, case=False, na=False)
        )

    filtered = df[mask].reset_index(drop=True)
    logger.info(f"🔍 General RSS articles mentioning {ticker}: {len(filtered)}")
    return filtered


def fetch_all_news_for_ticker(
    ticker: str,
    company_name: str = "",
) -> pd.DataFrame:
    """
    Main function to call from the pipeline.
    Combines:
      1. General RSS feeds filtered by ticker/aliases
      2. Yahoo Finance per-ticker RSS (ticker-specific)

    Returns a single deduplicated DataFrame.
    """
    # 1. General RSS — broad market news filtered to this ticker
    general_df = fetch_all_news()
    filtered_general = filter_by_ticker(general_df, ticker, company_name)

    # 2. Yahoo per-ticker RSS — articles specifically about this ticker
    yahoo_ticker_df = fetch_yahoo_ticker_news(ticker)

    # 3. Combine and deduplicate
    frames = []
    if not filtered_general.empty:
        frames.append(filtered_general)
    if not yahoo_ticker_df.empty:
        frames.append(yahoo_ticker_df)

    if not frames:
        logger.warning(f"No news articles found for {ticker}")
        return pd.DataFrame()

    combined = pd.concat(frames, ignore_index=True)
    combined = combined.drop_duplicates(subset=["title"]).reset_index(drop=True)

    logger.info(
        f"📊 {ticker} total news: {len(combined)} articles "
        f"(RSS filtered: {len(filtered_general)}, "
        f"Yahoo ticker: {len(yahoo_ticker_df)})"
    )
    return combined