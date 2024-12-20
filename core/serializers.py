from rest_framework import serializers
from core.models import CryptoPair, Strategy


class CryptoPairSerializer(serializers.ModelSerializer):
    class Meta:
        model = CryptoPair
        fields = ["id", "name", "base_currency", "quote_currency"]


class StrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = Strategy
        fields = ["id", "user", "risk_level", "amount", "expected_return", "created_at"]
