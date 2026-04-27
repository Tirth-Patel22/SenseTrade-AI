from django.conf import settings
from django.db import models


class Ticker(models.Model):
    symbol = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=255, blank=True)
    exchange = models.CharField(max_length=64, blank=True)
    sector = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.symbol


class PriceHistory(models.Model):
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE, related_name="prices")
    date = models.DateField(db_index=True)
    open = models.DecimalField(max_digits=12, decimal_places=4)
    high = models.DecimalField(max_digits=12, decimal_places=4)
    low = models.DecimalField(max_digits=12, decimal_places=4)
    close = models.DecimalField(max_digits=12, decimal_places=4)
    volume = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["ticker", "date"], name="uniq_ticker_date_price")
        ]
        ordering = ["-date"]


class NewsHeadline(models.Model):
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE, related_name="news")
    source = models.CharField(max_length=64)
    title = models.CharField(max_length=512)
    description = models.TextField(blank=True)
    url = models.URLField()
    published_at = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published_at"]


class SentimentLog(models.Model):
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE, related_name="sentiments")
    headline = models.ForeignKey(NewsHeadline, on_delete=models.CASCADE, related_name="sentiments")
    label = models.CharField(max_length=16)
    score = models.FloatField()
    analyzed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-analyzed_at"]


class DailySentiment(models.Model):
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE, related_name="daily_sentiments")
    date = models.DateField(db_index=True)
    average_score = models.FloatField()
    headline_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["ticker", "date"], name="uniq_ticker_date_sentiment")
        ]
        ordering = ["-date"]


class PredictionLog(models.Model):
    SIGNAL_CHOICES = [
        ("BUY", "Buy"),
        ("SELL", "Sell"),
        ("HOLD", "Hold"),
    ]

    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE, related_name="predictions")
    signal = models.CharField(max_length=8, choices=SIGNAL_CHOICES)
    confidence = models.FloatField()
    forecast_price = models.DecimalField(max_digits=12, decimal_places=4)
    input_window = models.PositiveIntegerField(default=30)
    model_version = models.CharField(max_length=64, default="hybrid-lstm-finbert-v1")
    explanation = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class WatchlistItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="watchlist_items")
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE, related_name="watchers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "ticker"], name="uniq_user_watchlist_ticker")
        ]


class PortfolioPosition(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="portfolio_positions")
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE, related_name="positions")
    quantity = models.DecimalField(max_digits=14, decimal_places=4)
    average_buy_price = models.DecimalField(max_digits=12, decimal_places=4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "ticker"], name="uniq_user_portfolio_ticker")
        ]

