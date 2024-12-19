from rest_framework import viewsets
from core.models import CryptoPair, Strategy
from core.serializers import CryptoPairSerializer, StrategySerializer


class CryptoPairViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CryptoPair.objects.all()
    serializer_class = CryptoPairSerializer


class StrategyViewSet(viewsets.ModelViewSet):
    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer
