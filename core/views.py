from rest_framework import viewsets, filters
from core.models import CryptoPair, Strategy
from core.serializers import CryptoPairSerializer, StrategySerializer


class CryptoPairViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CryptoPair.objects.all()
    serializer_class = CryptoPairSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


class StrategyViewSet(viewsets.ModelViewSet):
    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
