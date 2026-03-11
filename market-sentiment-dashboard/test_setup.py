import os

import pandas as pd
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

# Test yfinance (network required)
print("yfinance imported")
try:
    ticker = yf.Ticker("AAPL")
    hist = ticker.history(period="5d")
    if hist.empty:
        print("yfinance request returned no data (network/rate-limit/symbol issue).")
    else:
        print("yfinance fetched AAPL data")
        print(hist[["Close"]].tail(3))
except Exception as exc:
    print(f"yfinance fetch failed: {exc}")

# Test env vars loaded
key = os.getenv("NEWSAPI_KEY")
prefix = key[:4] if key and key != "your_key_here" else "⚠️ not set yet"
print(f"\n.env loaded — NewsAPI key starts with: {prefix}")

print("\nSetup complete!")
