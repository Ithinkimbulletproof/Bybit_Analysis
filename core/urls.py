from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    CryptoPairViewSet,
    StrategyViewSet,
    generate_strategy_view,
    pair_list_view,
    strategy_list_view,
)

router = DefaultRouter()
router.register(r"crypto-pairs", CryptoPairViewSet, basename="crypto-pair")
router.register(r"strategies", StrategyViewSet, basename="strategy")

urlpatterns = [
    path("", include(router.urls)),
    path("generate-strategy/", generate_strategy_view, name="generate_strategy"),
    path("crypto-pairs/", pair_list_view, name="pair_list"),
    path("strategies/", strategy_list_view, name="strategy_list"),
]
