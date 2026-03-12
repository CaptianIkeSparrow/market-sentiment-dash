import numpy as np
import pandas as pd
from loguru import logger


def compute_sentiment_score(df: pd.DataFrame) -> float:
    """
    Compute a single sentiment score from -1 (very negative)
    to +1 (very positive) for a set of articles.

    Weights each article by its confidence score so
    high-confidence predictions matter more.
    """
    if df.empty:
        return 0.0

    scores: list[float] = []
    for _, row in df.iterrows():
        sentiment = row.get("sentiment")
        positive = float(row.get("positive", 0.0) or 0.0)
        negative = float(row.get("negative", 0.0) or 0.0)
        confidence = float(row.get("confidence", 0.0) or 0.0)

        if sentiment == "positive":
            numeric = positive - negative
        elif sentiment == "negative":
            numeric = negative - positive
            numeric = -numeric
        else:
            numeric = 0.0

        weighted = numeric * confidence
        scores.append(weighted)

    return round(float(np.mean(scores)), 4)


def aggregate_sentiment(df: pd.DataFrame, ticker: str) -> dict:
    """
    Aggregate sentiment across all sources into a
    summary report for a ticker.
    """
    if df.empty:
        return {"ticker": ticker, "overall_score": 0.0, "signal": "neutral"}

    overall_score = compute_sentiment_score(df)

    source_scores: dict[str, float] = {}
    if "source" in df.columns:
        for source in df["source"].dropna().unique():
            source_df = df[df["source"] == source]
            source_scores[str(source)] = compute_sentiment_score(source_df)

    sentiment_counts = (
        df["sentiment"].value_counts().to_dict() if "sentiment" in df.columns else {}
    )
    total = len(df)

    if overall_score > 0.15:
        signal = "bullish"
    elif overall_score < -0.15:
        signal = "bearish"
    else:
        signal = "neutral"

    recent = df.head(max(1, len(df) // 3))
    recent_score = compute_sentiment_score(recent)
    velocity = round(recent_score - overall_score, 4)

    report = {
        "ticker": ticker,
        "overall_score": overall_score,
        "signal": signal,
        "sentiment_velocity": velocity,
        "total_articles": total,
        "positive_pct": round(sentiment_counts.get("positive", 0) / total * 100, 1),
        "negative_pct": round(sentiment_counts.get("negative", 0) / total * 100, 1),
        "neutral_pct": round(sentiment_counts.get("neutral", 0) / total * 100, 1),
        "source_breakdown": source_scores,
    }

    logger.info(f"{ticker} sentiment: {signal} (score: {overall_score})")
    return report
