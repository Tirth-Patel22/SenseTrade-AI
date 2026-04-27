from collections import defaultdict

import numpy as np
from django.db.models import Avg, Count
from sklearn.preprocessing import MinMaxScaler
from transformers import pipeline

from apps.core.models import PriceHistory, SentimentLog, Ticker

_SENTIMENT_PIPELINE = None


def get_finbert_pipeline():
    global _SENTIMENT_PIPELINE
    if _SENTIMENT_PIPELINE is None:
        _SENTIMENT_PIPELINE = pipeline("text-classification", model="ProsusAI/finbert")
    return _SENTIMENT_PIPELINE


def analyze_headline_sentiment(text: str):
    if not text:
        return "neutral", 0.0
    predictor = get_finbert_pipeline()
    output = predictor(text[:512])[0]
    label = output["label"].lower()
    score = float(output["score"])
    signed_score = score if label == "positive" else -score if label == "negative" else 0.0
    return label, signed_score


def aggregate_daily_sentiment(ticker: Ticker):
    rows = (
        SentimentLog.objects.filter(ticker=ticker)
        .values("headline__published_at__date")
        .annotate(average_score=Avg("score"), headline_count=Count("id"))
    )
    payload = {}
    for row in rows:
        payload[row["headline__published_at__date"]] = {
            "average_score": float(row["average_score"] or 0.0),
            "headline_count": int(row["headline_count"] or 0),
        }
    return payload


def build_hybrid_features(ticker: Ticker, window_size: int = 30):
    prices = (
        PriceHistory.objects.filter(ticker=ticker)
        .order_by("date")
        .values_list("date", "open", "high", "low", "close", "volume")
    )
    if len(prices) < window_size + 1:
        raise ValueError("Not enough price points for hybrid feature window")

    closes = np.array([float(p[4]) for p in prices], dtype=np.float32).reshape(-1, 1)
    scaler = MinMaxScaler()
    normalized = scaler.fit_transform(closes).flatten()

    daily_sentiment = defaultdict(float)
    for date, stats in aggregate_daily_sentiment(ticker).items():
        daily_sentiment[date] = float(stats["average_score"])

    features = []
    targets = []
    dates = [p[0] for p in prices]
    for idx in range(window_size, len(normalized)):
        price_window = normalized[idx - window_size : idx]
        sentiment_window = np.array([daily_sentiment[d] for d in dates[idx - window_size : idx]], dtype=np.float32)
        stacked = np.column_stack([price_window, sentiment_window])
        features.append(stacked)
        targets.append(normalized[idx])

    return np.array(features), np.array(targets), scaler, dates[-1]


def build_lstm_model(window_size: int, feature_count: int = 2):
    model = Sequential(
        [
            LSTM(64, return_sequences=True, input_shape=(window_size, feature_count)),
            Dropout(0.2),
            LSTM(32),
            Dropout(0.2),
            Dense(16, activation="relu"),
            Dense(1),
        ]
    )
    model.compile(optimizer="adam", loss="mse")
    return model


def predict_signal_for_ticker(ticker_symbol: str, window_size: int = 30):
    ticker = Ticker.objects.get(symbol=ticker_symbol.upper())
    x, y, scaler, _ = build_hybrid_features(ticker=ticker, window_size=window_size)
    # services.py inside predict_signal_for_ticker(...)
    try:
        model = build_lstm_model(window_size=window_size, feature_count=x.shape[2])
        model.fit(x, y, epochs=3, batch_size=16, verbose=0)
        latest_sequence = x[-1].reshape(1, x.shape[1], x.shape[2])
        next_close_scaled = float(model.predict(latest_sequence, verbose=0)[0][0])
    except Exception:
        next_close_scaled = float(np.mean(y[-5:])) if len(y) >= 5 else float(y[-1])
    forecast_price = float(scaler.inverse_transform(np.array([[next_close_scaled]])).flatten()[0])

    current_close = float(
        PriceHistory.objects.filter(ticker=ticker).order_by("-date").values_list("close", flat=True).first()
    )
    delta = (forecast_price - current_close) / current_close if current_close else 0.0
    if delta > 0.01:
        signal = "BUY"
    elif delta < -0.01:
        signal = "SELL"
    else:
        signal = "HOLD"

    confidence = min(0.95, max(0.5, abs(delta) * 10 + 0.5))
    explain_rows = (
        SentimentLog.objects.filter(ticker=ticker)
        .select_related("headline")
        .order_by("-analyzed_at")[:5]
    )
    explanations = [
        {"headline": row.headline.title, "score": row.score, "label": row.label}
        for row in explain_rows
    ]

    return {
        "signal": signal,
        "confidence": round(confidence, 4),
        "price_forecast": round(forecast_price, 4),
        "current_price": round(current_close, 4),
        "explanations": explanations,
        "window_size": window_size,
        "model_version": "hybrid-lstm-finbert-v1",
    }

