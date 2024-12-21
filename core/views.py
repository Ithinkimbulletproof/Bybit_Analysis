from django.shortcuts import render
from rest_framework import viewsets, filters
from core.models import CryptoPair, Strategy
from core.serializers import CryptoPairSerializer, StrategySerializer


def generate_strategy_view(request):
    if request.method == "POST":
        amount = request.POST.get("amount")
        risk_level = request.POST.get("risk_level")

        from core.analytics import generate_strategy

        strategy = generate_strategy(float(amount), risk_level)

        return render(request, "core/generate_strategy.html", {"strategy": strategy})

    return render(request, "core/generate_strategy.html")


def pair_list_view(request):
    from core.models import CryptoPair

    pairs = CryptoPair.objects.all()
    return render(request, "core/pair_list.html", {"pairs": pairs})


def strategy_list_view(request):
    from core.models import Strategy

    strategies = Strategy.objects.filter(user=request.user)
    return render(request, "core/strategies.html", {"strategies": strategies})


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
