from django.contrib.auth.models import User
from rest_framework import serializers

from apps.core.models import PortfolioPosition, PredictionLog, PriceHistory, Ticker, WatchlistItem


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        return user


class TickerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticker
        fields = ["id", "symbol", "name", "exchange", "sector"]


class PriceHistorySerializer(serializers.ModelSerializer):
    ticker = serializers.SlugRelatedField(read_only=True, slug_field="symbol")

    class Meta:
        model = PriceHistory
        fields = ["ticker", "date", "open", "high", "low", "close", "volume"]


class WatchlistItemSerializer(serializers.ModelSerializer):
    ticker = TickerSerializer(read_only=True)
    ticker_symbol = serializers.CharField(write_only=True)

    class Meta:
        model = WatchlistItem
        fields = ["id", "ticker", "ticker_symbol", "created_at"]
        read_only_fields = ["id", "created_at", "ticker"]

    def create(self, validated_data):
        symbol = validated_data.pop("ticker_symbol").upper()
        ticker, _ = Ticker.objects.get_or_create(symbol=symbol)
        return WatchlistItem.objects.create(
            user=self.context["request"].user,
            ticker=ticker,
            **validated_data,
        )


class PortfolioPositionSerializer(serializers.ModelSerializer):
    ticker = TickerSerializer(read_only=True)
    ticker_symbol = serializers.CharField(write_only=True)

    class Meta:
        model = PortfolioPosition
        fields = ["id", "ticker", "ticker_symbol", "quantity", "average_buy_price", "updated_at"]
        read_only_fields = ["id", "updated_at", "ticker"]

    def create(self, validated_data):
        symbol = validated_data.pop("ticker_symbol").upper()
        ticker, _ = Ticker.objects.get_or_create(symbol=symbol)
        return PortfolioPosition.objects.create(
            user=self.context["request"].user,
            ticker=ticker,
            **validated_data,
        )


class PredictionLogSerializer(serializers.ModelSerializer):
    ticker = serializers.SlugRelatedField(read_only=True, slug_field="symbol")

    class Meta:
        model = PredictionLog
        fields = [
            "id",
            "ticker",
            "signal",
            "confidence",
            "forecast_price",
            "model_version",
            "explanation",
            "created_at",
        ]

