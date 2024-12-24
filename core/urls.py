from django.urls import path
from core import views

urlpatterns = [
    path("", views.api_home, name="api_home"),
    path("generate-strategy/", views.generate_strategy_view, name="generate_strategy"),
    path("crypto-pairs/", views.pair_list_view, name="pair_list"),
    path("strategies/", views.strategy_list_view, name="strategy_list"),
]
