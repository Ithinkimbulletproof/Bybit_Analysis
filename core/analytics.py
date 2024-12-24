import sys
import numpy as np
import pandas as pd
from pyti.relative_strength_index import relative_strength_index as rsi
from pyti.simple_moving_average import simple_moving_average as sma
from core.models import HistoricalData, CryptoPair
import logging
import traceback

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def calculate_volatility(pair_name, period=None):
    try:
        historical_data = HistoricalData.objects.filter(pair__name=pair_name).order_by(
            "-date"
        )

        data = pd.DataFrame(list(historical_data.values("date", "close_price")))

        if period:
            data = data.head(period)

        if len(data) < 2:
            return None

        results = {}
        periods = [period] if period else [30, 90, 180, 365]

        for p in periods:
            if len(data) >= p:
                period_data = data.head(p)
                returns = np.diff(np.log(period_data["close_price"].values))
                volatility = np.std(returns)
                results[f"volatility_{p}_days"] = round(volatility, 4)
            else:
                results[f"volatility_{p}_days"] = None

        logger.info(f"Волатильность для {pair_name} рассчитана: {results}")
        return results
    except Exception as e:
        logger.error(f"Ошибка при расчёте волатильности для {pair_name}: {e}")
        logger.error(traceback.format_exc())
        return None


def calculate_technical_indicators(pair_name):
    try:
        historical_data = HistoricalData.objects.filter(pair__name=pair_name).order_by(
            "-date"
        )

        data = pd.DataFrame(list(historical_data.values("date", "close_price")))

        if len(data) < 30:
            return None

        prices = data["close_price"].values

        sma_50 = sma(prices[-50:], 50)[-1] if len(data) >= 50 else None
        sma_200 = sma(prices, 200)[-1] if len(data) >= 200 else None
        rsi_14 = rsi(prices[-14:], 14)[-1] if len(data) >= 14 else None

        prediction = None
        if sma_50 and sma_200:
            if sma_50 > sma_200 and rsi_14 < 70:
                prediction = "up"
            elif sma_50 < sma_200 and rsi_14 > 30:
                prediction = "down"
            else:
                prediction = "neutral"

        indicators = {
            "sma_50": sma_50,
            "sma_200": sma_200,
            "rsi_14": rsi_14,
            "prediction": prediction,
        }
        logger.info(f"Технические индикаторы для {pair_name}: {indicators}")
        return indicators
    except Exception as e:
        logger.error(f"Ошибка при расчёте индикаторов для {pair_name}: {e}")
        logger.error(traceback.format_exc())
        return None


def update_trend(pair_name, trend):
    try:
        pair = CryptoPair.objects.get(name=pair_name)
        if pair.trend != trend:
            pair.trend = trend
            pair.save()
            logger.info(f"Обновлен тренд для пары {pair_name}: {trend}")
    except CryptoPair.DoesNotExist:
        logger.error(f"Пара {pair_name} не найдена в базе")


def update_volatility(pair, volatility):
    try:
        if volatility.get("volatility_30_days"):
            pair.volatility_30_days = volatility["volatility_30_days"]
        if volatility.get("volatility_90_days"):
            pair.volatility_90_days = volatility["volatility_90_days"]
        if volatility.get("volatility_180_days"):
            pair.volatility_180_days = volatility["volatility_180_days"]
        if volatility.get("volatility_365_days"):
            pair.volatility_365_days = volatility["volatility_365_days"]

        pair.save()
        logger.info(f"Волатильность для пары {pair.name} обновлена в базе.")
    except Exception as e:
        logger.error(f"Ошибка при обновлении волатильности для пары {pair.name}: {e}")


def analyze_and_update_trends():
    try:
        pairs = CryptoPair.objects.all()

        for pair in pairs:
            logger.info(f"Запуск анализа для пары {pair.name}")

            indicators = calculate_technical_indicators(pair.name)
            volatility = calculate_volatility(pair.name)

            if indicators:
                trend = indicators.get("prediction", "neutral")
                update_trend(pair.name, trend)
                logger.info(f"Тренд для пары {pair.name} обновлен: {trend}")

            if volatility:
                update_volatility(pair, volatility)
                logger.info(f"Волатильность для пары {pair.name}: {volatility}")

    except Exception as e:
        logger.error(f"Ошибка при анализе и обновлении трендов: {e}")
