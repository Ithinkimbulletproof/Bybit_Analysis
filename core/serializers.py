from rest_framework import serializers
from core.models import CryptoPair, Strategy


class CryptoPairSerializer(serializers.ModelSerializer):
    class Meta:
        model = CryptoPair
        fields = "__all__"


class StrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = Strategy
        fields = "__all__"
