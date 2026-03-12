import requests
import pandas as pd
from datetime import datetime, timezone
from loguru import logger


def fetch_stocktwits(ticker: str) -> pd.DataFrame:
    """
    Fetch recent messages from Stocktwits for a ticker.
    Completely public — no API key needed.
    """
    try:
        url = f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json"
        response = requests.get(
            url,
            headers={"User-Agent": "market-sentiment-dashboard/1.0"},
            timeout=10,
        )
        if not response.ok:
            logger.error(
                f"❌ Stocktwits {ticker}: HTTP {response.status_code} {response.reason}"
            )
            return pd.DataFrame()

        try:
            data = response.json()
        except Exception:
            snippet = response.text[:200].replace("\n", " ")
            logger.error(f"❌ Stocktwits {ticker}: non-JSON response: {snippet!r}")
            return pd.DataFrame()

        messages = data.get("messages", [])
        results = []

        for msg in messages:
            sentiment = None
            if msg.get("entities", {}).get("sentiment"):
                sentiment = msg["entities"]["sentiment"].get("basic")

            results.append(
                {
                    "source": "stocktwits",
                    "title": msg.get("body", ""),
                    "summary": "",
                    "url": f"https://stocktwits.com/message/{msg.get('id')}",
                    "score": msg.get("likes", {}).get("total", 0),
                    "num_comments": 0,
                    "sentiment_label": sentiment,
                    "published": msg.get("created_at", ""),
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }
            )

        logger.info(f"✅ Stocktwits {ticker}: {len(results)} messages fetched")
        return pd.DataFrame(results)

    except Exception as e:
        logger.error(f"❌ Failed to fetch Stocktwits for {ticker}: {e}")
        return pd.DataFrame()


def fetch_finviz_news(ticker: str) -> pd.DataFrame:
    """
    Fetch news from Finviz for a specific ticker.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = f"https://finviz.com/quote.ashx?t={ticker}"
        response = requests.get(url, headers=headers, timeout=10)

        from html.parser import HTMLParser

        class FinvizParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.news = []
                self.in_news = False
                self.current_link = None
                self.current_time = None

            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if (
                    tag == "a"
                    and "class" in attrs
                    and "tab-link-news" in attrs.get("class", "")
                ):
                    self.current_link = attrs.get("href", "")
                    self.in_news = True

            def handle_data(self, data):
                if self.in_news and data.strip():
                    self.news.append(
                        {
                            "source": "finviz",
                            "title": data.strip(),
                            "summary": "",
                            "url": self.current_link,
                            "score": 0,
                            "sentiment_label": None,
                            "published": datetime.now(timezone.utc).isoformat(),
                            "fetched_at": datetime.now(timezone.utc).isoformat(),
                        }
                    )
                    self.in_news = False

        parser = FinvizParser()
        parser.feed(response.text)

        df = pd.DataFrame(parser.news)
        logger.info(f"✅ Finviz {ticker}: {len(df)} articles fetched")
        return df

    except Exception as e:
        logger.error(f"❌ Failed to fetch Finviz news for {ticker}: {e}")
        return pd.DataFrame()


def fetch_all_social(ticker: str) -> pd.DataFrame:
    """Fetch from all social/community sources for a ticker."""
    dfs = []

    stocktwits_df = fetch_stocktwits(ticker)
    if not stocktwits_df.empty:
        dfs.append(stocktwits_df)

    finviz_df = fetch_finviz_news(ticker)
    if not finviz_df.empty:
        dfs.append(finviz_df)

    if not dfs:
        logger.warning(f"No social data fetched for {ticker}")
        return pd.DataFrame()

    combined = pd.concat(dfs, ignore_index=True)
    logger.info(f"💬 Total social signals for {ticker}: {len(combined)}")
    return combined
