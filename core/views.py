import logging
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from core.models import CryptoPair, HistoricalData
from core.utils import (
    calculate_volatility,
    calculate_ta_indicators,
    generate_strategy_for_risk_level,
)
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def crypto_analytics_view(request):
    logger.debug("Запрос на криптоаналитику принят.")

    pairs = CryptoPair.objects.all()
    results = []

    for pair in pairs:
        logger.debug(f"Обрабатываем пару: {pair.name}")

        historical_data = HistoricalData.objects.filter(pair=pair).order_by("date")
        if not historical_data.exists():
            logger.warning(f"Нет исторических данных для пары {pair.name}")
            continue

        df = pd.DataFrame(list(historical_data.values("date", "close_price")))
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)
        df = calculate_ta_indicators(df)
        df["log_return"] = np.log(df["close_price"] / df["close_price"].shift(1))

        recent_returns = df["log_return"].tail(30)
        probability_of_growth = (recent_returns > 0).mean()
        expected_change = recent_returns.mean()
        trend = "вверх" if expected_change > 0 else "вниз"

        logger.debug(
            f"Вероятность роста для {pair.name}: {probability_of_growth * 100:.2f}%"
        )
        logger.debug(
            f"Ожидаемое изменение для {pair.name}: {expected_change * 100:.2f}%"
        )

        volatility = calculate_volatility(pair.name)

        results.append(
            {
                "pair": pair.name,
                "probability": round(probability_of_growth * 100, 2),
                "expected_change": round(expected_change * 100, 2),
                "trend": trend,
                "volatility_30": (
                    round(volatility["30d_volatility"], 2) if volatility else None
                ),
                "volatility_90": (
                    round(volatility["90d_volatility"], 2) if volatility else None
                ),
                "volatility_180": (
                    round(volatility["180d_volatility"], 2) if volatility else None
                ),
                "volatility_365": (
                    round(volatility["365d_volatility"], 2) if volatility else None
                ),
            }
        )

    sorted_results = sorted(results, key=lambda x: x["probability"], reverse=True)[:10]

    logger.debug("Возвращаем топ 10 результатов.")
    return render(
        request,
        "core/crypto_analytics.html",
        {
            "crypto_pairs": sorted_results,
        },
    )


def crypto_pairs_view(request):
    logger.debug("Запрос на криптовалютные пары принят.")
    pairs = CryptoPair.objects.values_list("name", flat=True)
    return JsonResponse(list(pairs), safe=False)


class StrategyAPIView(APIView):
    def post(self, request, *args, **kwargs):
        logger.debug("Запрос на стратегию принят.")
        risk_level = request.data.get("risk_level")
        amount = request.data.get("amount")

        logger.debug(f"Уровень риска: {risk_level}, Сумма: {amount}")

        strategy = generate_strategy_for_risk_level(risk_level)
        strategy["investment_amount"] = amount

        logger.debug(f"Сгенерированная стратегия: {strategy}")
        return Response(strategy)
