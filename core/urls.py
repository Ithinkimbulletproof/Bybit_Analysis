from rest_framework.routers import DefaultRouter
from core.views import CryptoPairViewSet, StrategyViewSet

router = DefaultRouter()
router.register(r"crypto-pairs", CryptoPairViewSet, basename="crypto-pair")
router.register(r"strategies", StrategyViewSet, basename="strategy")

urlpatterns = router.urls
