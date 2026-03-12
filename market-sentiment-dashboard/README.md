# Market Sentiment Dashboard

End-to-end project for ingesting market/news/social data, running sentiment + anomaly detection, ranking signals, and generating LLM summaries.

## What this project does

For a given ticker (e.g. `AAPL`), the pipeline:

1. Ingests **news headlines** (RSS) and **social/community chatter** (Stocktwits + Finviz)
2. Runs **FinBERT** (financial-language sentiment) over each headline/post
3. Aggregates individual predictions into a single **ticker-level signal** (bullish / bearish / neutral)
4. Computes **sentiment velocity** (are recent items more extreme than the overall baseline?) for anomaly detection later

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file (already scaffolded) if you want to add optional keys later.

## Quick check

```bash
python test_setup.py
```

## Data ingestion

### News (RSS)

- Implementation: `src/ingestion/news_fetcher.py`
- Output schema (DataFrame): `source`, `title`, `summary`, `url`, `published`, `fetched_at`
- Current sources include CNBC, MarketWatch, Yahoo Finance, Benzinga, InvestorPlace, Motley Fool (plus Reuters if resolvable in your environment).

Run:

```bash
python notebooks/test_ingestion.py
```

### Social/community signals

- Implementation: `src/ingestion/social_fetcher.py`
- Sources:
  - **Stocktwits** (public API, no auth): provides optional `sentiment_label` (“Bullish”/“Bearish”) from users
  - **Finviz** (scraped): provides a large stream of ticker-specific headlines

This gives us both:
- text to score with FinBERT, and
- a small “free” labeled subset (Stocktwits tags) to sanity-check model behavior.

### Price data

- Implementation: `src/ingestion/price_fetcher.py`
- Primary: `yfinance`
- Fallback: Stooq (used automatically when Yahoo rate-limits)

## Sentiment analysis (FinBERT)

### Per-item scoring

- Implementation: `src/nlp/sentiment.py`
- Model: `ProsusAI/finbert`
- Adds columns: `sentiment`, `confidence`, `positive`, `negative`, `neutral`

We score `title + summary` for each row for better signal than headline-only.

### Cleaning Stocktwits text

Stocktwits posts often contain many tickers (e.g. `$AAPL $AMZN $SPY`) and URLs, which can distract FinBERT.
We clean these before inference (remove `$TICKER`, strip URLs, normalize whitespace) to improve text quality.

### Aggregation into a ticker signal

- Implementation: `src/nlp/aggregator.py`
- Output: `overall_score` in `[-1, +1]`, `signal` (bullish/bearish/neutral), `sentiment_velocity`, per-source breakdown

## Interpreting results

### Why Stocktwits agreement can be low (and why that’s okay)

Stocktwits labels are **noisy**:

- Users sometimes tag *Bullish* while venting (“hate this market”), or tag *Bearish* because they’re short (a “positive” trade for them).
- FinBERT reads the full message; strong words like “hate” can dominate even when the post contains multiple tickers.
- Small samples (e.g. ~10 labeled posts) aren’t statistically stable — agreement improves with 50+ labeled posts.

Calling this out is a feature, not a bug: it shows the project treats social labels as a **weak validation signal**, not ground truth.

### The real signal to watch

The most useful output for downstream anomaly detection is typically:

- `overall_score`: baseline sentiment (neutral range is roughly `[-0.15, +0.15]`)
- `sentiment_velocity`: whether *recent* items are more positive/negative than the overall baseline
- `source_breakdown`: e.g. retail (Stocktwits) vs news (Finviz/RSS)

In practice, “slightly bearish + accelerating negativity” is exactly the kind of regime shift Step 4 anomaly detection should flag.

## Test the whole pipeline

```bash
python notebooks/test_sentiment.py
```

The first run downloads FinBERT weights and can take ~30–60 seconds.
