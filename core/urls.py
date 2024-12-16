from django.urls import path
from . import views

urlpatterns = [
    path("", views.crypto_analytics_view, name="crypto_analytics"),
    path("crypto-pairs/", views.crypto_pairs_view, name="crypto_pairs"),
    path("get-strategy/", views.StrategyAPIView.as_view(), name="get_strategy"),
]
