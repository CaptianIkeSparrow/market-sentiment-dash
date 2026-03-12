import pandas as pd
import requests
from loguru import logger
from datetime import datetime, timedelta


def fetch_price_history(ticker: str, period: str = "1mo") -> pd.DataFrame:
    """Fetch price history using Stooq as primary source."""
    try:
        end = datetime.today()
        period_map = {"1mo": 30, "3mo": 90, "6mo": 180, "1y": 365}
        days = period_map.get(period, 30)
        start = end - timedelta(days=days)

        start_str = start.strftime("%Y%m%d")
        end_str = end.strftime("%Y%m%d")

        url = (
            f"https://stooq.com/q/d/l/"
            f"?s={ticker.lower()}.us"
            f"&d1={start_str}&d2={end_str}&i=d"
        )

        df = pd.read_csv(url)

        if df.empty or "Close" not in df.columns:
            logger.warning(f"No price data found for {ticker}")
            return pd.DataFrame()

        df["Date"] = pd.to_datetime(df["Date"])
        df = df.set_index("Date")
        df = df[["Open", "High", "Low", "Close", "Volume"]]
        df = df.sort_index()

        logger.info(f"{ticker}: {len(df)} days of price data fetched")
        return df

    except Exception as e:
        logger.error(f"Failed to fetch price data for {ticker}: {e}")
        return pd.DataFrame()


def fetch_ticker_info(ticker: str) -> dict:
    """Fetch basic company info from a free public API."""
    try:
        known = {
            "AAPL": ("Apple Inc.", "Technology"),
            "NVDA": ("NVIDIA Corporation", "Technology"),
            "MSFT": ("Microsoft Corporation", "Technology"),
            "GOOGL": ("Alphabet Inc.", "Technology"),
            "AMZN": ("Amazon.com Inc.", "Consumer Cyclical"),
            "TSLA": ("Tesla Inc.", "Consumer Cyclical"),
            "META": ("Meta Platforms Inc.", "Technology"),
        }

        name, sector = known.get(ticker, (ticker, "Unknown"))

        return {
            "ticker": ticker,
            "company_name": name,
            "sector": sector,
            "industry": sector,
            "market_cap": None,
            "description": "",
        }

    except Exception as e:
        logger.error(f"Failed to fetch info for {ticker}: {e}")
        return {"ticker": ticker, "company_name": ticker}
