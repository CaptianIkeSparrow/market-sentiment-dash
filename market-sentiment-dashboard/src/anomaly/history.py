from datetime import datetime, timedelta

import numpy as np
import pandas as pd


def simulate_historical_scores(
    days: int = 30,
    base_mean: float = 0.05,
    base_std: float = 0.12,
    seed: int = 42,
) -> list[float]:
    """
    Simulate historical daily sentiment scores for testing.
    In production this would be read from a database.
    """
    np.random.seed(seed)
    scores = np.random.normal(loc=base_mean, scale=base_std, size=days)
    scores = np.clip(scores, -1.0, 1.0)
    return scores.tolist()


def simulate_historical_counts(
    days: int = 30,
    base_mean: float = 80,
    base_std: float = 20,
    seed: int = 42,
) -> list[int]:
    """
    Simulate historical daily article counts for testing.
    """
    np.random.seed(seed)
    counts = np.random.normal(loc=base_mean, scale=base_std, size=days)
    counts = np.clip(counts, 10, 300).astype(int)
    return counts.tolist()


def build_history_dataframe(
    ticker: str,
    days: int = 30,
) -> pd.DataFrame:
    """Build a historical DataFrame for display purposes."""
    scores = simulate_historical_scores(days=days)
    counts = simulate_historical_counts(days=days)

    dates = [datetime.now() - timedelta(days=i) for i in range(days, 0, -1)]

    return pd.DataFrame(
        {
            "date": dates,
            "ticker": ticker,
            "sentiment_score": scores,
            "article_count": counts,
        }
    )

