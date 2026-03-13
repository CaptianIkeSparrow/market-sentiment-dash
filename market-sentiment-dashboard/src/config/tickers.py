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
    "UCO": "proshares ultra bloomberg crude oil",

    # ── Crypto-adjacent ────────────────────────────────────────
    "MSTR": "MicroStrategy",
    "MARA": "Marathon Digital",
    "RIOT": "Riot Platforms",
#SECOND BLOCK MAY be more overlap fix later 
    # ── Energy — Oil shock beneficiaries ──────────────────────────────────
"XOM": "ExxonMobil",
"CVX": "Chevron",
"COP": "ConocoPhillips",
"OXY": "Occidental Petroleum",
"PSX": "Phillips 66",
"MPC": "Marathon Petroleum",
"VLO": "Valero Energy",
"EOG": "EOG Resources",
"DVN": "Devon Energy",
"PXD": "Pioneer Natural Resources",

# ── LNG ───────────────────────────────────────────────────────────────
"LNG": "Cheniere Energy",
"AR": "Antero Resources",
"EQT": "EQT Corporation",
"CTRA": "Coterra Energy",
"RRC": "Range Resources",

# ── Oil Services ──────────────────────────────────────────────────────
"HAL": "Halliburton",
"BKR": "Baker Hughes",
"NOV": "NOV Inc",
"WFRD": "Weatherford International",

# ── Defense ───────────────────────────────────────────────────────────
"LMT": "Lockheed Martin",
"NOC": "Northrop Grumman",
"RTX": "RTX Corporation",
"GD": "General Dynamics",
"LHX": "L3Harris Technologies",
"KTOS": "Kratos Defense",
"AXON": "Axon Enterprise",
"LDOS": "Leidos",
"SAIC": "Science Applications International",
"HII": "Huntington Ingalls Industries",
"TDG": "TransDigm Group",
"HEI": "HEICO Corporation",

# ── Airlines ──────────────────────────────────────────────────────────
"DAL": "Delta Air Lines",
"UAL": "United Airlines",
"AAL": "American Airlines",
"LUV": "Southwest Airlines",
"JBLU": "JetBlue Airways",
"ALK": "Alaska Air Group",

# ── Biotech ───────────────────────────────────────────────────────────
"BNTX": "BioNTech",
"NVAX": "Novavax",
"VRTX": "Vertex Pharmaceuticals",
"REGN": "Regeneron",
"BIIB": "Biogen",
"IONS": "Ionis Pharmaceuticals",
"CRSP": "CRISPR Therapeutics",
"BEAM": "Beam Therapeutics",
"EDIT": "Editas Medicine",

# ── Gold & Miners ─────────────────────────────────────────────────────
"GDX": "VanEck Gold Miners ETF",
"GDXJ": "VanEck Junior Gold Miners ETF",
"NEM": "Newmont Corporation",
"AEM": "Agnico Eagle Mines",
"GOLD": "Barrick Gold",
"KGC": "Kinross Gold",

# ── Utilities ─────────────────────────────────────────────────────────
"NEE": "NextEra Energy",
"SO": "Southern Company",
"DUK": "Duke Energy",
"AEP": "American Electric Power",
"EXC": "Exelon",

# ── Bonds ─────────────────────────────────────────────────────────────
"IEF": "7-10yr Treasury Bond ETF",

# ── Crypto Proxies ────────────────────────────────────────────────────
"CLSK": "CleanSpark",

# ── Financials ────────────────────────────────────────────────────────
"AIG": "American International Group",
"MET": "MetLife",
"PRU": "Prudential Financial",
}

# ── Your personal watchlist ────────────────────────────────
# Edit this list to change which tickers watchlist.py scans
WATCHLIST = [
    
    "XOM", "CVX", "COP", "OXY", "PSX",
    "MPC", "VLO", "EOG", "DVN", "PXD",
    "LNG", "AR", "EQT", "CTRA", "RRC",
    "SLB", "HAL", "BKR", "NOV", "WFRD",
    "LMT", "NOC", "RTX", "GD", "LHX",
    "KTOS", "AXON", "LDOS", "SAIC", "HII",
    "TDG", "HEI", "BA",
    "DAL", "UAL", "AAL", "LUV", "JBLU", "ALK",
    "MRNA", "BNTX", "NVAX", "VRTX", "REGN",
    "BIIB", "IONS", "CRSP", "BEAM", "EDIT",
    "GLD", "GDX", "GDXJ", "NEM", "AEM",
    "GOLD", "KGC",
    "NEE", "SO", "DUK", "AEP", "EXC",
    "TLT", "IEF",
    "NVDA", "AMD", "TSLA", "META", "AMZN",
    "GOOGL", "MSFT", "AAPL", "NFLX", "CRM",
    "MSTR", "MARA", "RIOT", "COIN", "CLSK",
    "PLTR", "CRWD", "NET", "DDOG", "SNOW",
    "JPM", "BAC", "GS", "MS", "C",
    "AIG", "MET", "PRU",

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