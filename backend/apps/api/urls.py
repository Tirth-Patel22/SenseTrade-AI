from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import LoginView, PortfolioViewSet, RegisterView, WatchlistViewSet, market_data, predict_ticker

router = DefaultRouter()
router.register("watchlist", WatchlistViewSet, basename="watchlist")
router.register("portfolio", PortfolioViewSet, basename="portfolio")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("market/<str:ticker>/", market_data, name="market-data"),
    path("predict/<str:ticker>/", predict_ticker, name="predict-ticker"),
]

