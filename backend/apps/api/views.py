from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from apps.core.models import DailySentiment, PortfolioPosition, PredictionLog, PriceHistory, Ticker, WatchlistItem

from .serializers import (
    PortfolioPositionSerializer,
    PriceHistorySerializer,
    RegisterSerializer,
    WatchlistItemSerializer,
)


class LoginView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class WatchlistViewSet(viewsets.ModelViewSet):
    serializer_class = WatchlistItemSerializer

    def get_queryset(self):
        return WatchlistItem.objects.filter(user=self.request.user).select_related("ticker")


class PortfolioViewSet(viewsets.ModelViewSet):
    serializer_class = PortfolioPositionSerializer

    def get_queryset(self):
        return PortfolioPosition.objects.filter(user=self.request.user).select_related("ticker")


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def market_data(request, ticker: str):
    symbol = ticker.upper()
    ticker_obj = Ticker.objects.filter(symbol=symbol).first()
    if not ticker_obj:
        return Response({"detail": "Ticker not found."}, status=status.HTTP_404_NOT_FOUND)

    prices = PriceHistory.objects.filter(ticker=ticker_obj).order_by("date")[:120]
    sentiments = DailySentiment.objects.filter(ticker=ticker_obj).order_by("date")[:120]
    sentiment_map = {s.date.isoformat(): s.average_score for s in sentiments}

    price_payload = PriceHistorySerializer(prices, many=True).data
    for row in price_payload:
        row["sentiment_score"] = sentiment_map.get(str(row["date"]), 0.0)

    return Response({"ticker": symbol, "candles": price_payload}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def predict_ticker(request, ticker: str):
    symbol = ticker.upper()
    try:
        from apps.ai.services import predict_signal_for_ticker
        payload = predict_signal_for_ticker(symbol)
    except Ticker.DoesNotExist:
        return Response({"detail": "Ticker not found."}, status=status.HTTP_404_NOT_FOUND)
    except ValueError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    ticker_obj = Ticker.objects.get(symbol=symbol)
    PredictionLog.objects.create(
        ticker=ticker_obj,
        signal=payload["signal"],
        confidence=payload["confidence"],
        forecast_price=Decimal(str(payload["price_forecast"])),
        model_version=payload["model_version"],
        explanation={"headlines": payload["explanations"]},
    )
    return Response(payload, status=status.HTTP_200_OK)

