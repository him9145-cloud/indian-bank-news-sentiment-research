"""Data validation, sentiment scoring, and return alignment for the research app."""

from __future__ import annotations

from datetime import time
from functools import lru_cache
from typing import Iterable

import numpy as np
import pandas as pd

NEWS_REQUIRED = {"published_at", "ticker", "headline"}
PRICE_REQUIRED = {"date", "ticker", "close"}
MARKET_CLOSE_IST = time(15, 30)

POSITIVE = {"beat", "benefit", "better", "growth", "improve", "increased", "increase", "profit", "record", "strong", "surge", "upgrade", "positive", "expand", "expanded", "robust"}
NEGATIVE = {"bad", "breach", "decline", "default", "downgrade", "fall", "fraud", "loss", "lower", "penalty", "provision", "risk", "weak", "worse", "negative", "stress", "slump", "higher"}


def _check_columns(frame: pd.DataFrame, required: Iterable[str], label: str) -> None:
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        raise ValueError(f"{label} CSV is missing required columns: {', '.join(missing)}")


def score_lexicon(texts: list[str]) -> list[dict[str, float]]:
    """Simple transparent baseline; returns normalized positive/neutral/negative scores."""
    rows = []
    for text in texts:
        words = {w.strip(".,!?;:()[]{}\"'").lower() for w in str(text).split()}
        score = len(words & POSITIVE) - len(words & NEGATIVE)
        polarity = float(np.tanh(score / 2))
        rows.append({"positive": max(polarity, 0.0), "negative": max(-polarity, 0.0), "neutral": 1 - abs(polarity)})
    return rows


@lru_cache(maxsize=1)
def _finbert_classifier():
    """Load one classifier per app process; weights download on first call."""
    from transformers import pipeline

    return pipeline("text-classification", model="ProsusAI/finbert", tokenizer="ProsusAI/finbert", top_k=None, truncation=True)


def score_finbert(texts: list[str]) -> list[dict[str, float]]:
    """Score using ProsusAI/finbert; weights download on first call."""
    classifier = _finbert_classifier()
    outputs = classifier([str(t)[:4000] for t in texts], batch_size=16)
    normalized = []
    for output in outputs:
        row = {str(item["label"]).lower(): float(item["score"]) for item in output}
        normalized.append({label: row.get(label, 0.0) for label in ("positive", "neutral", "negative")})
    return normalized


def analyze(news: pd.DataFrame, prices: pd.DataFrame, model: str = "FinBERT") -> tuple[pd.DataFrame, pd.DataFrame]:
    news = news.copy()
    prices = prices.copy()
    news.columns = [str(c).strip().lower() for c in news.columns]
    prices.columns = [str(c).strip().lower() for c in prices.columns]
    _check_columns(news, NEWS_REQUIRED, "News")
    _check_columns(prices, PRICE_REQUIRED, "Price")
    if "text" not in news:
        news["text"] = ""
    news["headline"] = news["headline"].fillna("").astype(str)
    news["text"] = news["text"].fillna("").astype(str)
    news["content"] = (news["headline"] + ". " + news["text"]).str.strip(" .")
    news["ticker"] = news["ticker"].astype(str).str.upper().str.strip()
    # Naive timestamps are explicitly interpreted as IST; aware timestamps are converted to IST.
    def to_ist(value: object) -> pd.Timestamp:
        timestamp = pd.Timestamp(value)
        if pd.isna(timestamp):
            return pd.NaT
        if timestamp.tzinfo is None:
            return timestamp.tz_localize("Asia/Kolkata", ambiguous="NaT", nonexistent="shift_forward")
        return timestamp.tz_convert("Asia/Kolkata")

    timestamps = news["published_at"].map(to_ist)
    if timestamps.isna().any():
        raise ValueError("Some news publication timestamps could not be parsed.")
    news["published_at"] = timestamps

    prices["date"] = pd.to_datetime(prices["date"], errors="coerce").dt.normalize()
    prices["ticker"] = prices["ticker"].astype(str).str.upper().str.strip()
    prices["close"] = pd.to_numeric(prices["close"], errors="coerce")
    prices = prices.dropna(subset=["date", "ticker", "close"]).sort_values(["ticker", "date"])
    if prices.duplicated(["ticker", "date"]).any():
        raise ValueError("Price CSV must contain at most one row per ticker and trading date.")
    prices["return"] = prices.groupby("ticker")["close"].pct_change()
    prices["next_return"] = prices.groupby("ticker")["return"].shift(-1)
    if "benchmark_close" in prices:
        prices["benchmark_close"] = pd.to_numeric(prices["benchmark_close"], errors="coerce")
        prices["benchmark_return"] = prices.groupby("ticker")["benchmark_close"].pct_change()
        prices["abnormal_return"] = prices["return"] - prices["benchmark_return"]
        prices["next_abnormal_return"] = prices.groupby("ticker")["abnormal_return"].shift(-1)
    else:
        prices["abnormal_return"] = prices["return"]
        prices["next_abnormal_return"] = prices.groupby("ticker")["return"].shift(-1)

    if model == "FinBERT":
        scores = score_finbert(news["content"].tolist())
    else:
        scores = score_lexicon(news["content"].tolist())
    score_frame = pd.DataFrame(scores, index=news.index)
    news = pd.concat([news, score_frame], axis=1)
    news["sentiment"] = news[["positive", "neutral", "negative"]].idxmax(axis=1)
    news["sentiment_score"] = news["positive"] - news["negative"]

    exchange_dates = {ticker: pd.DatetimeIndex(group["date"].sort_values().unique()) for ticker, group in prices.groupby("ticker")}
    assigned = []
    for row in news.itertuples():
        dt = row.published_at
        session_date = dt.tz_localize(None).normalize()
        if dt.time() > MARKET_CLOSE_IST:
            session_date += pd.Timedelta(days=1)
        sessions = exchange_dates.get(row.ticker, pd.DatetimeIndex([]))
        position = sessions.searchsorted(session_date, side="left")
        assigned.append(sessions[position] if position < len(sessions) else pd.NaT)
    news["event_date"] = assigned
    market_cols = ["date", "ticker", "return", "next_return", "abnormal_return", "next_abnormal_return"]
    if "volume" in prices:
        prices["volume"] = pd.to_numeric(prices["volume"], errors="coerce")
        prices["volume_median"] = prices.groupby("ticker")["volume"].transform(lambda s: s.shift(1).rolling(20, min_periods=5).median())
        prices["relative_volume"] = prices["volume"] / prices["volume_median"]
        market_cols += ["volume", "relative_volume"]
    results = news.merge(prices[market_cols], left_on=["event_date", "ticker"], right_on=["date", "ticker"], how="left")
    summary = results.groupby(["event_date", "ticker"], dropna=False, as_index=False).agg(
        article_count=("headline", "size"), mean_sentiment=("sentiment_score", "mean"),
        positive_share=("positive", lambda x: float((x > 0.5).mean())),
        abnormal_return=("abnormal_return", "first"), next_abnormal_return=("next_abnormal_return", "first"),
    )
    return results, summary
