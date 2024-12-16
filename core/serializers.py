from rest_framework import serializers
from core.models import Strategy


class CryptoPairAnalyticsSerializer(serializers.Serializer):
    pair = serializers.CharField()
    probability = serializers.FloatField()
    expected_change = serializers.FloatField()
    trend = serializers.CharField()


class StrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = Strategy
        fields = ["risk_level", "parameters", "expected_return"]
