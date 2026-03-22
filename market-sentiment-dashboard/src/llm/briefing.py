import os
from dataclasses import dataclass

import anthropic
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


@dataclass
class AnalystBriefing:
    """A structured analyst briefing for a ticker."""

    ticker: str
    headline: str
    situation: str
    sentiment_analysis: str
    risk_flags: str
    outlook: str
    raw_response: str


def build_prompt(
    ticker: str,
    company_name: str,
    sentiment_report: dict,
    sentiment_anomaly,
    volume_anomaly,
    price_data,
    sample_headlines: list[str],
) -> str:
    """
    Build a structured prompt for the LLM briefing.
    The more context we give the LLM, the better the output.
    """
    if not price_data.empty and len(price_data) >= 2:
        latest_close = float(price_data["Close"].iloc[-1])
        prev_close = float(price_data["Close"].iloc[-2])
        price_change = ((latest_close - prev_close) / prev_close) * 100
        price_str = f"${latest_close:.2f} ({price_change:+.2f}% today)"
    else:
        price_str = "unavailable"

    headlines_str = "\n".join([f"- {h}" for h in sample_headlines[:8]])

    source_breakdown = sentiment_report.get("source_breakdown", {})
    sources_str = "\n".join(
        [f"- {source}: {score:+.3f}" for source, score in source_breakdown.items()]
    )

    prompt = f"""You are a senior financial analyst writing a concise market intelligence briefing.
Analyze the following data and write a professional briefing for {company_name} ({ticker}).

## Current Market Data
- Stock Price: {price_str}
- Overall Sentiment Score: {sentiment_report['overall_score']} (scale: -1.0 bearish to +1.0 bullish)
- Sentiment Signal: {sentiment_report['signal'].upper()}
- Sentiment Velocity: {sentiment_report['sentiment_velocity']} (positive = sentiment improving, negative = deteriorating)
- Total Articles Analyzed: {sentiment_report['total_articles']}

## Sentiment Breakdown
- Positive articles: {sentiment_report['positive_pct']}%
- Negative articles: {sentiment_report['negative_pct']}%
- Neutral articles: {sentiment_report['neutral_pct']}%

## Source Sentiment Scores
{sources_str}

## Anomaly Detection
- Sentiment Anomaly: {sentiment_anomaly.severity.upper()} (z-score: {sentiment_anomaly.z_score})
  {sentiment_anomaly.description}
- Volume Anomaly: {volume_anomaly.severity.upper()} (z-score: {volume_anomaly.z_score})
  {volume_anomaly.description}

## Sample Headlines from Today
{headlines_str}

## Your Task
Write a structured analyst briefing with exactly these four sections:

HEADLINE: (one punchy sentence summarizing the situation)

SITUATION: (2-3 sentences describing what the data shows is happening right now, state the date of our stock info)

SENTIMENT ANALYSIS: (2-3 sentences interpreting what the sentiment scores and anomalies mean in plain English)

RISK FLAGS: (2-3 bullet points of specific things to watch)

OUTLOOK: (1-2 sentences forward-looking summary. Final sentance state buy, sell or hold and confidence rating out of 10)

Be direct, specific, and professional. Reference actual numbers from the data.
Do not add any other sections or commentary outside these five."""

    return prompt


def generate_briefing(
    ticker: str,
    company_name: str,
    sentiment_report: dict,
    sentiment_anomaly,
    volume_anomaly,
    price_data,
    scored_df,
) -> AnalystBriefing:
    """
    Generate a full analyst briefing using Claude.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing ANTHROPIC_API_KEY. Add it to your `.env` as "
            "`ANTHROPIC_API_KEY=...`."
        )

    def generate_briefing(
    ticker: str,
    company_name: str,
    sentiment_report: dict,
    sentiment_anomaly,
    volume_anomaly,
    price_data,
    scored_df,
) -> AnalystBriefing:
        import anthropic

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    sample_headlines = scored_df["title"].dropna().head(8).tolist()
    prompt = build_prompt(
        ticker=ticker,
        company_name=company_name,
        sentiment_report=sentiment_report,
        sentiment_anomaly=sentiment_anomaly,
        volume_anomaly=volume_anomaly,
        price_data=price_data,
        sample_headlines=sample_headlines,
    )

    logger.info(f"Generating analyst briefing for {ticker}...")

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )



def parse_briefing(ticker: str, raw_text: str) -> AnalystBriefing:
    """Parse the LLM response into structured sections."""
    import re

    # Strip markdown bold markers and normalize section headers
    cleaned = re.sub(r'\*+', '', raw_text)

    sections = {
        "headline": "",
        "situation": "",
        "sentiment_analysis": "",
        "risk_flags": "",
        "outlook": "",
    }

    current_section = None
    buffer = []

    for line in cleaned.split("\n"):
        line = line.strip()
        if not line:
            continue

        upper = line.upper()

        if "HEADLINE:" in upper:
            if current_section:
                sections[current_section] = " ".join(buffer).strip()
            current_section = "headline"
            buffer = [line.split(":", 1)[-1].strip()]

        elif "SITUATION:" in upper:
            if current_section:
                sections[current_section] = " ".join(buffer).strip()
            current_section = "situation"
            buffer = [line.split(":", 1)[-1].strip()]

        elif "SENTIMENT ANALYSIS:" in upper:
            if current_section:
                sections[current_section] = " ".join(buffer).strip()
            current_section = "sentiment_analysis"
            buffer = [line.split(":", 1)[-1].strip()]

        elif "RISK FLAGS:" in upper:
            if current_section:
                sections[current_section] = " ".join(buffer).strip()
            current_section = "risk_flags"
            buffer = [line.split(":", 1)[-1].strip()]

        elif "OUTLOOK:" in upper:
            if current_section:
                sections[current_section] = " ".join(buffer).strip()
            current_section = "outlook"
            buffer = [line.split(":", 1)[-1].strip()]

        else:
            buffer.append(line)

    if current_section and buffer:
        sections[current_section] = " ".join(buffer).strip()

    return AnalystBriefing(
        ticker=ticker,
        headline=sections["headline"],
        situation=sections["situation"],
        sentiment_analysis=sections["sentiment_analysis"],
        risk_flags=sections["risk_flags"],
        outlook=sections["outlook"],
        raw_response=raw_text,
    )


def print_briefing(briefing: AnalystBriefing):
    """Pretty print the briefing to terminal."""
    divider = "=" * 60

    print(f"\n{divider}")
    print(f"  MARKET INTELLIGENCE BRIEFING — {briefing.ticker}")
    print(f"{divider}")
    print(f"\n📌 {briefing.headline}\n")
    print(f"📊 SITUATION\n{briefing.situation}\n")
    print(f"🧠 SENTIMENT ANALYSIS\n{briefing.sentiment_analysis}\n")
    print(f"⚠️  RISK FLAGS\n{briefing.risk_flags}\n")
    print(f"🔭 OUTLOOK\n{briefing.outlook}")
    print(f"\n{divider}\n")

