from django.contrib import admin

from .models import (
    DailySentiment,
    NewsHeadline,
    PortfolioPosition,
    PredictionLog,
    PriceHistory,
    SentimentLog,
    Ticker,
    WatchlistItem,
)

admin.site.register(Ticker)
admin.site.register(PriceHistory)
admin.site.register(NewsHeadline)
admin.site.register(SentimentLog)
admin.site.register(DailySentiment)
admin.site.register(PredictionLog)
admin.site.register(WatchlistItem)
admin.site.register(PortfolioPosition)

