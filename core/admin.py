from django.contrib import admin
from .models import User, CryptoPair, HistoricalData, Strategy


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "risk_level")


@admin.register(CryptoPair)
class CryptoPairAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "base_currency", "quote_currency")


@admin.register(HistoricalData)
class HistoricalDataAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "pair",
        "date",
        "open_price",
        "close_price",
        "high_price",
        "low_price",
        "volume",
    )


@admin.register(Strategy)
class StrategyAdmin(admin.ModelAdmin):
    list_display = ("id", "risk_level", "expected_return")
