from datetime import datetime
import requests

import yfinance as yf
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.ai.services import analyze_headline_sentiment, aggregate_daily_sentiment
from apps.core.models import DailySentiment, NewsHeadline, PriceHistory, SentimentLog, Ticker


class Command(BaseCommand):
    help = "Fetch daily OHLCV + financial news and persist sentiment logs"

    def add_arguments(self, parser):
        parser.add_argument("--ticker", type=str, required=True, help="Ticker symbol, example: AAPL")
        parser.add_argument("--period", type=str, default="6mo", help="yfinance period")
        parser.add_argument("--news-limit", type=int, default=20, help="Max headlines to fetch")

    @transaction.atomic
    def handle(self, *args, **options):
        symbol = options["ticker"].upper().strip()
        period = options["period"]
        news_limit = options["news_limit"]

        ticker, _ = Ticker.objects.get_or_create(symbol=symbol)

        self._ingest_prices(ticker, period)
        self._ingest_news_and_sentiment(ticker, news_limit)
        self.stdout.write(self.style.SUCCESS(f"Ingestion complete for {symbol}"))

    def _ingest_prices(self, ticker: Ticker, period: str):
        df = yf.Ticker(ticker.symbol).history(period=period)
        if df.empty:
            self.stdout.write(self.style.WARNING(f"No price data returned for {ticker.symbol}"))
            return

        for idx, row in df.iterrows():
            PriceHistory.objects.update_or_create(
                ticker=ticker,
                date=idx.date(),
                defaults={
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]) if row["Volume"] else 0,
                },
            )

    def _ingest_news_and_sentiment(self, ticker: Ticker, news_limit: int):
        feed = self._fetch_news(ticker.symbol, news_limit)
        for item in feed:
            published = item.get("publishedAt")
            published_dt = datetime.fromisoformat(published.replace("Z", "+00:00")) if published else datetime.utcnow()

            headline = NewsHeadline.objects.create(
            ticker=ticker,
            source=((item.get("source") or {}).get("name") or "unknown")[:64],
            title=(item.get("title") or "")[:512],
            description=item.get("description") or "",
            url=item.get("url") or "",
            published_at=published_dt,
            )


            label, score = analyze_headline_sentiment(headline.title)
            SentimentLog.objects.create(
                ticker=ticker,
                headline=headline,
                label=label,
                score=score,
            )

        for date, values in aggregate_daily_sentiment(ticker).items():
            DailySentiment.objects.update_or_create(
                ticker=ticker,
                date=date,
                defaults={
                    "average_score": values["average_score"],
                    "headline_count": values["headline_count"],
                },
            )

    def _fetch_news(self, symbol: str, limit: int):
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": symbol,
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": limit,
        }
        api_key = self._get_env("NEWS_API_KEY")
        if api_key:
            params["apiKey"] = api_key

        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            return response.json().get("articles", [])
        except Exception:
            # Falls back to an empty list when external API is unavailable.
            return []

    @staticmethod
    def _get_env(key: str):
        import os

        return os.getenv(key)

