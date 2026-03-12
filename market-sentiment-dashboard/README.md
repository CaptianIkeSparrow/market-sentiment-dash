# Market Sentiment & Signal Dashboard

An end-to-end financial intelligence pipeline that monitors real-time news and social media for any stock ticker, runs sentiment analysis using a fine-tuned financial NLP model, detects statistical anomalies, and generates professional analyst briefings using an LLM.

## Demo

```bash
python app.py NVDA
```

```text
Starting Market Sentiment Analysis for NVDA...

Fetching data...
✅ 136 total signals collected
   • 6 news articles
   • 130 social signals

Running sentiment analysis...
✅ Sentiment: NEUTRAL (score: 0.0101)
   • Positive: 22.1%
   • Negative: 19.9%
   • Neutral:  58.1%

Running anomaly detection...
✅ Anomaly detected: HIGH
   - Unusual spike in coverage — 136 articles vs average of 76 (severe anomaly)

Generating analyst briefing...

============================================================
  MARKET INTELLIGENCE BRIEFING — NVDA
============================================================

Nvidia treading water amid elevated media scrutiny and
   structural options-driven volatility.

SITUATION
NVDA closed at $186.03 (+0.69%) with a severe anomaly in
coverage volume — 136 articles vs a 76-article average...

SENTIMENT ANALYSIS
Sentiment remains balanced but fragile, with deteriorating
velocity suggesting investor caution is building...

RISK FLAGS
- Options-driven volatility concentrated in weeklies
- Negative sentiment velocity of -0.161
- Narrative fragmentation across institutional sources

OUTLOOK
Nvidia faces near-term consolidation pressure as options
mechanics and narrative deterioration offset fundamentals...

============================================================

Latest Price: $186.03 (+0.69% today)
```

## How It Works

The pipeline has five stages that run in sequence:

1. **Data Ingestion** — Fetches real-time financial news from RSS feeds (CNBC, MarketWatch, Yahoo Finance, Benzinga, InvestorPlace, Motley Fool), social signals from Stocktwits and Finviz, and price history from Stooq.
2. **Sentiment Analysis** — Runs every article and social post through FinBERT, a BERT model fine-tuned on financial text. Each piece of content gets scored as positive, negative, or neutral with a confidence value. Scores are aggregated into a single weighted sentiment signal from `-1.0` (very bearish) to `+1.0` (very bullish).
3. **Anomaly Detection** — Uses z-score analysis to flag when today’s sentiment or article volume is statistically unusual compared to historical baselines. A z-score above `2.0` triggers a moderate anomaly; above `2.5` triggers a severe one. Volume spikes are particularly valuable — a sudden surge in coverage often precedes meaningful price moves.
4. **LLM Briefing** — Feeds all signals into Claude (Anthropic) to generate a structured five-section analyst briefing: headline, situation, sentiment analysis, risk flags, and outlook. The LLM references actual numbers from the data, not generic commentary.
5. **CLI Output** — Everything prints to terminal in a clean, readable format. Run any ticker in `tickers.py`, or pass a custom company name as a second argument.

## Architecture

```text
python app.py TICKER
        │
        ├── src/ingestion/
        │     ├── news_fetcher.py       RSS feeds (CNBC, MarketWatch, Yahoo, Benzinga, InvestorPlace, Motley Fool)
        │     ├── social_fetcher.py     Stocktwits + Finviz
        │     └── price_fetcher.py      Stooq price history
        │
        ├── src/nlp/
        │     ├── sentiment.py          FinBERT inference + batch processing
        │     └── aggregator.py         Weighted sentiment score + velocity
        │
        ├── src/anomaly/
        │     ├── detector.py           Z-score anomaly detection
        │     └── history.py            Historical baseline simulation
        │
        ├── src/llm/
        │     └── briefing.py           LLM prompt engineering + structured parsing
        │
        └── src/config/
              └── tickers.py            80+ pre-mapped tickers by sector
```

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| NLP Model | FinBERT (`ProsusAI/finbert`) via HuggingFace Transformers |
| ML Framework | PyTorch |
| LLM | Claude (Anthropic API) |
| News Data | RSS feeds via `feedparser` |
| Social Data | Stocktwits API + Finviz |
| Price Data | Stooq |
| Anomaly Detection | Z-score (`scipy`) |
| Data Processing | `pandas`, `numpy` |

## Setup

### Prerequisites

- Python 3.11+
- Git

### Installation

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/market-sentiment-dashboard.git
cd market-sentiment-dashboard

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\\Scripts\\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### API Keys

Create a `.env` file in the project root:

```bash
ANTHROPIC_API_KEY=your_key_here
```

Get your Anthropic API key at `console.anthropic.com`.

## Run

```bash
# Analyze any ticker
python app.py NVDA
python app.py AAPL
python app.py TSLA

# Pass a custom company name
python app.py CRWD CrowdStrike

# List all supported tickers
python app.py --list
```

## Supported Tickers

80+ tickers pre-mapped across sectors. Run `python app.py --list` to see all of them, or edit `src/config/tickers.py` to add your own.

Sectors covered: Big Tech, Finance, Healthcare, Consumer, Energy, EV & Clean Energy, AI & Cloud, Indices & ETFs, Crypto-adjacent.

## Sentiment Score Explained

Every article is scored by FinBERT as positive, negative, or neutral with a confidence value. The overall score is computed as:

```text
score = weighted_average(positive_prob - negative_prob) × confidence
```

The result is a single number from `-1.0` to `+1.0`:

```text
-1.0 ── -0.15 ── 0.0 ── +0.15 ── +1.0
very    bearish  neutral  bullish   very
bearish                            bullish
```

Sentiment velocity measures whether recent articles are more extreme than the historical average — a negative velocity means conditions are deteriorating even if the overall score is still neutral.

## Anomaly Detection

The z-score measures how many standard deviations the current value is from the historical mean:

```text
z = (current_value - historical_mean) / historical_std
```

| Z-score | Severity |
|---|---|
| < 1.5 | None — within normal range |
| 1.5 – 2.0 | Mild anomaly |
| 2.0 – 2.5 | Moderate anomaly |
| > 2.5 | Severe anomaly |

Both sentiment score and article volume are monitored independently. A volume spike without a sentiment shift can be an early warning signal before the narrative has fully formed.

## Project Structure

```text
market-sentiment-dashboard/
├── app.py                    # Main CLI entry point
├── requirements.txt
├── .env                      # API keys (not committed)
├── .gitignore
├── src/
│   ├── ingestion/
│   │   ├── news_fetcher.py
│   │   ├── social_fetcher.py
│   │   └── price_fetcher.py
│   ├── nlp/
│   │   ├── sentiment.py
│   │   └── aggregator.py
│   ├── anomaly/
│   │   ├── detector.py
│   │   └── history.py
│   ├── llm/
│   │   └── briefing.py
│   └── config/
│       └── tickers.py
├── notebooks/                # Development & testing scripts
│   ├── test_ingestion.py
│   ├── test_sentiment.py
│   ├── test_anomaly.py
│   └── test_briefing.py
└── data/
    ├── raw/
    └── processed/
```

## Limitations & Future Work

Current limitations:

- Historical baselines are simulated — a production version would store real daily scores in a database and pull actual history.
- RSS feeds provide general market news; ticker-specific coverage relies on Stocktwits and Finviz.

Planned improvements:

- Store daily sentiment scores in SQLite for real historical baselines.
- Add Streamlit UI for visual dashboard.
- Multi-ticker watchlist with scheduled daily runs.
- Backtest: correlate historical sentiment signals with price moves.
- Deploy to Hugging Face Spaces for public demo.
