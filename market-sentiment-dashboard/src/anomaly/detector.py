from dataclasses import dataclass

import numpy as np
import pandas as pd
from loguru import logger
from scipy import stats


@dataclass
class AnomalyResult:
    """Result of an anomaly check."""

    is_anomaly: bool
    severity: str  # "none", "mild", "moderate", "severe"
    z_score: float  # How many std devs from the mean
    current_value: float
    historical_mean: float
    historical_std: float
    direction: str  # "spike_positive", "spike_negative", "normal"
    description: str


def detect_sentiment_anomaly(
    historical_scores: list[float],
    current_score: float,
    threshold_mild: float = 1.5,
    threshold_moderate: float = 2.0,
    threshold_severe: float = 2.5,
) -> AnomalyResult:
    """
    Detect if current sentiment score is anomalous
    compared to historical scores.

    Uses z-score: how many standard deviations is the
    current value from the historical mean?
    """
    if len(historical_scores) < 3:
        return AnomalyResult(
            is_anomaly=False,
            severity="none",
            z_score=0.0,
            current_value=current_score,
            historical_mean=0.0,
            historical_std=0.0,
            direction="normal",
            description="Not enough historical data to detect anomalies yet.",
        )

    mean = float(np.mean(historical_scores))
    std = float(np.std(historical_scores))

    if std < 0.001:
        std = 0.001

    z_score = (current_score - mean) / std
    abs_z = abs(z_score)

    if abs_z >= threshold_severe:
        severity = "severe"
        is_anomaly = True
    elif abs_z >= threshold_moderate:
        severity = "moderate"
        is_anomaly = True
    elif abs_z >= threshold_mild:
        severity = "mild"
        is_anomaly = True
    else:
        severity = "none"
        is_anomaly = False

    if z_score > threshold_mild:
        direction = "spike_positive"
    elif z_score < -threshold_mild:
        direction = "spike_negative"
    else:
        direction = "normal"

    if not is_anomaly:
        description = f"Sentiment is within normal range (z={z_score:.2f})"
    elif direction == "spike_positive":
        description = (
            f"Unusually POSITIVE sentiment detected — "
            f"{abs_z:.1f} std devs above historical average "
            f"({severity} anomaly)"
        )
    else:
        description = (
            f"Unusually NEGATIVE sentiment detected — "
            f"{abs_z:.1f} std devs below historical average "
            f"({severity} anomaly)"
        )

    return AnomalyResult(
        is_anomaly=is_anomaly,
        severity=severity,
        z_score=round(float(z_score), 4),
        current_value=round(float(current_score), 4),
        historical_mean=round(mean, 4),
        historical_std=round(std, 4),
        direction=direction,
        description=description,
    )


def detect_volume_anomaly(
    historical_counts: list[int],
    current_count: int,
) -> AnomalyResult:
    """
    Detect if the current article/post volume for a ticker
    is unusually high — a spike in coverage often precedes
    or accompanies major price moves.
    """
    if len(historical_counts) < 3:
        return AnomalyResult(
            is_anomaly=False,
            severity="none",
            z_score=0.0,
            current_value=float(current_count),
            historical_mean=0.0,
            historical_std=0.0,
            direction="normal",
            description="Not enough historical data for volume anomaly detection.",
        )

    mean = float(np.mean(historical_counts))
    std = float(np.std(historical_counts))

    if std < 0.001:
        std = 0.001

    z_score = (current_count - mean) / std
    abs_z = abs(z_score)

    if abs_z >= 2.5:
        severity = "severe"
        is_anomaly = True
    elif abs_z >= 2.0:
        severity = "moderate"
        is_anomaly = True
    elif abs_z >= 1.5:
        severity = "mild"
        is_anomaly = True
    else:
        severity = "none"
        is_anomaly = False

    direction = "spike_positive" if z_score > 1.5 else "normal"

    if not is_anomaly:
        description = f"Article volume is normal ({current_count} articles)"
    else:
        description = (
            f"Unusual spike in coverage — {current_count} articles vs "
            f"average of {mean:.0f} ({severity} anomaly)"
        )

    return AnomalyResult(
        is_anomaly=is_anomaly,
        severity=severity,
        z_score=round(float(z_score), 4),
        current_value=float(current_count),
        historical_mean=round(mean, 4),
        historical_std=round(std, 4),
        direction=direction,
        description=description,
    )


def generate_alert(
    ticker: str,
    sentiment_anomaly: AnomalyResult,
    volume_anomaly: AnomalyResult,
    current_score: float,
) -> dict | None:
    """
    Generate a human-readable alert if anomalies are detected.
    Returns None if nothing notable is happening.
    """
    alerts: list[str] = []

    if sentiment_anomaly.is_anomaly:
        alerts.append(sentiment_anomaly.description)

    if volume_anomaly.is_anomaly:
        alerts.append(volume_anomaly.description)

    if not alerts:
        return None

    severities = [sentiment_anomaly.severity, volume_anomaly.severity]
    if "severe" in severities:
        level = "🔴 HIGH"
    elif "moderate" in severities:
        level = "🟡 MEDIUM"
    else:
        level = "🟢 LOW"

    return {
        "ticker": ticker,
        "alert_level": level,
        "current_sentiment_score": current_score,
        "alerts": alerts,
        "action": "Monitor closely" if "HIGH" in level else "Worth watching",
    }

