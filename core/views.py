import logging
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, filters
from core.models import CryptoPair, Strategy
from core.serializers import CryptoPairSerializer, StrategySerializer


logger = logging.getLogger(__name__)


def api_home(request):
    logger.info("Запрос на главную страницу API")
    try:
        return render(request, "core/home.html")
    except Exception as e:
        logger.exception(f"Ошибка при рендеринге главной страницы: {e}")
        return JsonResponse({"error": "Ошибка на сервере"}, status=500)


def generate_strategy_view(request):
    logger.info("Запрос на генерацию стратегии")
    if request.method == "POST":
        amount = request.POST.get("amount")
        risk_level = request.POST.get("risk_level")
        logger.info(f"Получены данные: amount={amount}, risk_level={risk_level}")

        try:
            strategy = generate_strategy(float(amount), risk_level)
            logger.info(f"Сгенерирована стратегия: {strategy}")
            return render(
                request, "core/generate_strategy.html", {"strategy": strategy}
            )
        except ValueError as e:
            logger.error(f"Ошибка при генерации стратегии: {e}")
            return render(request, "core/generate_strategy.html", {"error": str(e)})
        except Exception as e:
            logger.exception(f"Неизвестная ошибка: {e}")
            return render(
                request, "core/generate_strategy.html", {"error": "Ошибка на сервере"}
            )

    logger.warning("Генерация стратегии запрошена с неподдерживаемым методом.")
    return render(request, "core/generate_strategy.html")


def pair_list_view(request):
    logger.info("Запрос на список криптовалютных пар")
    try:
        pairs_grow = CryptoPair.objects.filter(trend="up")
        pairs_fall = CryptoPair.objects.filter(trend="down")

        logger.info(
            f"Криптовалюты: рост - {pairs_grow.count()}, падение - {pairs_fall.count()}"
        )

        return render(
            request,
            "core/pair_list.html",
            {
                "pairs_grow": pairs_grow,
                "pairs_fall": pairs_fall,
            },
        )
    except Exception as e:
        logger.exception(f"Ошибка при запросе списка пар: {e}")
        return JsonResponse({"error": "Ошибка на сервере"}, status=500)


@csrf_exempt
def toggle_favorite(request, pair_id):
    logger.info(f"Изменение избранного для пары с id {pair_id}")
    if request.method == "POST":
        try:
            pair = CryptoPair.objects.get(id=pair_id)
            pair.is_favorite = not pair.is_favorite
            pair.save()
            logger.info(f"Избранное изменено для пары {pair.name}: {pair.is_favorite}")
            return JsonResponse({"success": True})
        except CryptoPair.DoesNotExist:
            logger.error(f"Криптовалютная пара с id {pair_id} не найдена.")
            return JsonResponse({"success": False, "error": "Пара не найдена"})
        except Exception as e:
            logger.exception(f"Ошибка при изменении избранного для пары {pair_id}: {e}")
            return JsonResponse({"success": False, "error": "Ошибка на сервере"})
    logger.warning(f"Неподдерживаемый метод {request.method} для toggle_favorite")
    return JsonResponse({"success": False, "error": "Неподдерживаемый метод"})


def strategy_list_view(request):
    logger.info("Запрос на список стратегий")
    try:
        strategies = Strategy.objects.all()
        logger.info(f"Найдено стратегий: {strategies.count()}")
        return render(
            request,
            "core/strategies.html",
            {"strategies": strategies},
        )
    except Exception as e:
        logger.exception(f"Ошибка при запросе списка стратегий: {e}")
        return JsonResponse({"error": "Ошибка на сервере"}, status=500)


class CryptoPairViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CryptoPair.objects.all()
    serializer_class = CryptoPairSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    def list(self, request, *args, **kwargs):
        search_query = request.query_params.get("search", "")
        logger.info(f"Поиск криптовалютных пар: {search_query}")
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            logger.exception(f"Ошибка при поиске криптовалютных пар: {e}")
            return JsonResponse({"error": "Ошибка на сервере"}, status=500)


class StrategyViewSet(viewsets.ModelViewSet):
    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer

    def get_queryset(self):
        try:
            user_strategies = self.queryset.filter(user=self.request.user)
            logger.info(
                f"Стратегии пользователя {self.request.user.username}: {user_strategies.count()}"
            )
            return user_strategies
        except Exception as e:
            logger.exception(f"Ошибка при получении стратегий пользователя: {e}")
            return self.queryset.none()
