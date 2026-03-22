from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import pandas as pd
from loguru import logger
import re


MODEL_NAME = "ProsusAI/finbert"


def sentiment_bucket_5(score: float) -> str:
    """
    Bucket a continuous sentiment score into 5 labels.

    Score is expected to be in [-1, 1], typically computed as:
        positive_prob - negative_prob
    """
    if score <= -0.4:
        return "very_bear"
    if score <= -0.15:
        return "bear"
    if score < 0.15:
        return "neutral"
    if score < 0.4:
        return "bull"
    return "very_bull"


def clean_financial_text(text: str) -> str:
    """Clean social media financial text before sentiment analysis."""
    if not text:
        return ""
    text = re.sub(r"\$[A-Z]{1,5}", "", str(text))
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


class FinBERTAnalyzer:
    """
    Financial sentiment analyzer using FinBERT.
    Classifies text as positive, negative, or neutral
    with a confidence score.
    """

    def __init__(self):
        logger.info("Loading FinBERT model — this takes ~30 seconds first time...")
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        self.model.eval()

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        self.labels = ["positive", "negative", "neutral"]
        logger.info("✅ FinBERT loaded successfully")

    def analyze_text(self, text: str) -> dict:
        """
        Analyze a single piece of text.
        Returns sentiment label and confidence scores.
        """
        if not text or not text.strip():
            return {
                "sentiment": "neutral",
                "positive": 0.0,
                "negative": 0.0,
                "neutral": 1.0,
                "confidence": 1.0,
            }

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)

        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        probs = probs.squeeze().tolist()

        scores = {
            "positive": round(float(probs[0]), 4),
            "negative": round(float(probs[1]), 4),
            "neutral": round(float(probs[2]), 4),
        }

        sentiment = max(scores, key=scores.get)
        confidence = round(float(max(probs)), 4)
        score = round(float(scores["positive"] - scores["negative"]), 4)
        bucket_5 = sentiment_bucket_5(score)

        return {
            "sentiment": sentiment,
            "bucket_5": bucket_5,
            "score": score,
            "confidence": confidence,
            **scores,
        }

    def analyze_batch(self, texts: list[str], batch_size: int = 16) -> list[dict]:
        """
        Analyze a list of texts efficiently in batches.
        """
        results: list[dict] = []
        if not texts:
            return results

        total_batches = (len(texts) - 1) // batch_size + 1

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            batch = [t if t and t.strip() else "neutral" for t in batch]

            inputs = self.tokenizer(
                batch,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True,
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)

            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)

            for prob in probs:
                prob_list = prob.tolist()
                scores = {
                    "positive": round(float(prob_list[0]), 4),
                    "negative": round(float(prob_list[1]), 4),
                    "neutral": round(float(prob_list[2]), 4),
                }
                sentiment = max(scores, key=scores.get)
                confidence = round(float(max(prob_list)), 4)
                score = round(float(scores["positive"] - scores["negative"]), 4)
                bucket_5 = sentiment_bucket_5(score)
                results.append(
                    {
                        "sentiment": sentiment,
                        "bucket_5": bucket_5,
                        "score": score,
                        "confidence": confidence,
                        **scores,
                    }
                )

            logger.info(f"Analyzed batch {i // batch_size + 1} / {total_batches}")

        return results


def analyze_dataframe(df: pd.DataFrame, analyzer: FinBERTAnalyzer) -> pd.DataFrame:
    """
    Run sentiment analysis on a DataFrame of articles or posts.
    Analyzes the title + summary combined for best results.
    """
    if df.empty:
        return df

    title_series = df["title"] if "title" in df.columns else pd.Series([""] * len(df))
    summary_series = df["summary"] if "summary" in df.columns else pd.Series(
        [""] * len(df)
    )
    texts = (
        title_series.fillna("").apply(clean_financial_text)
        + " "
        + summary_series.fillna("").apply(clean_financial_text)
    ).tolist()

    logger.info(f"Running sentiment analysis on {len(texts)} texts...")
    results = analyzer.analyze_batch(texts)

    results_df = pd.DataFrame(results)
    out = pd.concat([df.reset_index(drop=True), results_df], axis=1)

    if "sentiment" in out.columns:
        counts = out["sentiment"].value_counts()
        logger.info(f"Sentiment breakdown: {counts.to_dict()}")

    return out
