from django.contrib import admin
from .models import CryptoPair, HistoricalData, Strategy, UserProfile, RiskLevel


@admin.register(CryptoPair)
class CryptoPairAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "base_currency", "quote_currency")
    search_fields = ("name", "base_currency", "quote_currency")
    list_filter = ("base_currency", "quote_currency")


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
    search_fields = ("pair__name",)
    list_filter = ("pair", "date")
    date_hierarchy = "date"


@admin.register(Strategy)
class StrategyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "risk_level",
        "amount",
        "expected_return",
        "created_at",
    )
    search_fields = ("user__username",)
    list_filter = ("risk_level", "created_at")
    date_hierarchy = "created_at"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "risk_level")
    search_fields = ("user__username",)
    list_filter = ("risk_level",)


@admin.register(RiskLevel)
class RiskLevelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("name",)
