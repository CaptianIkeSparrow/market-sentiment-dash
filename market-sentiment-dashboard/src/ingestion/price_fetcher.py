from io import StringIO

import pandas as pd
import requests
import yfinance as yf
from loguru import logger


def _fetch_price_history_stooq(ticker: str, period: str) -> pd.DataFrame:
    symbol = ticker.lower()
    if "." not in symbol:
        symbol = f"{symbol}.us"

    url = f"https://stooq.com/q/d/l/?s={symbol}&i=d"
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()

    df = pd.read_csv(StringIO(resp.text))
    if df.empty or "Date" not in df.columns:
        return pd.DataFrame()

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date").sort_index()

    end = df.index.max()
    if isinstance(end, pd.Timestamp) and pd.notna(end):
        try:
            if period.endswith("d"):
                cutoff = end - pd.Timedelta(days=int(period[:-1]))
                df = df[df.index >= cutoff]
            elif period.endswith("mo"):
                cutoff = end - pd.DateOffset(months=int(period[:-2]))
                df = df[df.index >= cutoff]
            elif period.endswith("y"):
                cutoff = end - pd.DateOffset(years=int(period[:-1]))
                df = df[df.index >= cutoff]
        except Exception:
            pass

    rename_map = {
        "Open": "Open",
        "High": "High",
        "Low": "Low",
        "Close": "Close",
        "Volume": "Volume",
        "Openint": "Openint",
    }
    df = df.rename(columns=rename_map)
    needed = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in df.columns]
    return df[needed]


def fetch_price_history(ticker: str, period: str = "3mo") -> pd.DataFrame:
    """
    Fetch historical price data for a ticker.
    period options: 1d, 5d, 1mo, 3mo, 6mo, 1y
    """
    try:
        df = yf.download(
            tickers=ticker,
            period=period,
            interval="1d",
            progress=False,
            auto_adjust=False,
            threads=False,
        )

        if df.empty:
            logger.warning(
                f"No price data found for {ticker} via yfinance; trying Stooq fallback"
            )
            try:
                df = _fetch_price_history_stooq(ticker, period=period)
            except Exception as e:
                logger.error(f"❌ Stooq fallback failed for {ticker}: {e}")
                return df

        df = df[["Open", "High", "Low", "Close", "Volume"]]
        df.index = pd.to_datetime(df.index)

        logger.info(f"📈 {ticker}: {len(df)} days of price data fetched")
        return df

    except Exception as e:
        logger.error(f"❌ Failed to fetch price data for {ticker}: {e}")
        return pd.DataFrame()


def fetch_ticker_info(ticker: str) -> dict:
    """Fetch basic company info for a ticker."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.get_info()

        return {
            "ticker": ticker,
            "company_name": info.get("longName", ticker),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
            "market_cap": info.get("marketCap", None),
            "description": info.get("longBusinessSummary", "")[:300],
        }

    except Exception as e:
        logger.error(f"❌ Failed to fetch info for {ticker}: {e}")
        return {
            "ticker": ticker,
            "company_name": ticker,
            "sector": "Unknown",
            "industry": "Unknown",
            "market_cap": None,
            "description": "",
        }
