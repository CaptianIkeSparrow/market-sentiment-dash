TICKER_MAP = {
    # ── Big Tech ───────────────────────────────────────────────
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Google",
    "GOOG": "Google",
    "AMZN": "Amazon",
    "META": "Meta",
    "NVDA": "Nvidia",
    "TSLA": "Tesla",
    "NFLX": "Netflix",
    "ORCL": "Oracle",
    "CRM": "Salesforce",
    "ADBE": "Adobe",
    "INTC": "Intel",
    "AMD": "AMD",
    "QCOM": "Qualcomm",
    "TXN": "Texas Instruments",
    "AVGO": "Broadcom",
    "MU": "Micron",
    "AMAT": "Applied Materials",
    "LRCX": "Lam Research",

    # ── Finance ────────────────────────────────────────────────
    "JPM": "JPMorgan Chase",
    "BAC": "Bank of America",
    "WFC": "Wells Fargo",
    "GS": "Goldman Sachs",
    "MS": "Morgan Stanley",
    "C": "Citigroup",
    "BLK": "BlackRock",
    "AXP": "American Express",
    "V": "Visa",
    "MA": "Mastercard",
    "PYPL": "PayPal",
    "SQ": "Block",
    "COIN": "Coinbase",

    # ── Healthcare ─────────────────────────────────────────────
    "JNJ": "Johnson & Johnson",
    "UNH": "UnitedHealth",
    "PFE": "Pfizer",
    "ABBV": "AbbVie",
    "MRK": "Merck",
    "LLY": "Eli Lilly",
    "BMY": "Bristol-Myers Squibb",
    "AMGN": "Amgen",
    "GILD": "Gilead Sciences",
    "MRNA": "Moderna",

    # ── Consumer ───────────────────────────────────────────────
    "WMT": "Walmart",
    "COST": "Costco",
    "TGT": "Target",
    "HD": "Home Depot",
    "LOW": "Lowe's",
    "MCD": "McDonald's",
    "SBUX": "Starbucks",
    "NKE": "Nike",
    "DIS": "Disney",
    "CMCSA": "Comcast",

    # ── Energy ─────────────────────────────────────────────────
    "XOM": "ExxonMobil",
    "CVX": "Chevron",
    "COP": "ConocoPhillips",
    "SLB": "Schlumberger",
    "EOG": "EOG Resources",

    # ── EV & Clean Energy ──────────────────────────────────────
    "RIVN": "Rivian",
    "LCID": "Lucid Motors",
    "NIO": "NIO",
    "XPEV": "XPeng",
    "ENPH": "Enphase Energy",
    "FSLR": "First Solar",

    # ── AI & Cloud ─────────────────────────────────────────────
    "PLTR": "Palantir",
    "SNOW": "Snowflake",
    "DDOG": "Datadog",
    "NET": "Cloudflare",
    "ZS": "Zscaler",
    "CRWD": "CrowdStrike",
    "AI": "C3.ai",
    "PATH": "UiPath",
    "GTLB": "GitLab",

    # ── Indices & ETFs ─────────────────────────────────────────
    "SPY": "S&P 500",
    "QQQ": "Nasdaq 100",
    "DIA": "Dow Jones",
    "IWM": "Russell 2000",
    "VTI": "Total Stock Market",
    "GLD": "Gold",
    "TLT": "20yr Treasury Bonds",

    # ── Crypto-adjacent ────────────────────────────────────────
    "MSTR": "MicroStrategy",
    "MARA": "Marathon Digital",
    "RIOT": "Riot Platforms",
}

# Default watchlist. Edit this list to add/remove tickers.
WATCHLIST = [
    "NVDA",
    "AAPL",
    "TSLA",
    "MSFT",
    "AMZN",
    "META",
    "GOOGL",
    "INTC",
    "AMD",
    "PLTR",
]


def get_company_name(ticker: str) -> str:
    """Look up company name for a ticker. Falls back to ticker if not found."""
    return TICKER_MAP.get(ticker.upper(), ticker.upper())


def list_supported_tickers() -> None:
    """Print all supported tickers."""
    print("\nSupported tickers:\n")
    for ticker, name in TICKER_MAP.items():
        print(f"  {ticker:<8} {name}")


def get_watchlist() -> list[tuple[str, str]]:
    """
    Returns watchlist as a list of (ticker, company_name) tuples.
    """
    return [(ticker, get_company_name(ticker)) for ticker in WATCHLIST]
