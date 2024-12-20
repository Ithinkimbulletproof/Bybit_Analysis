import numpy as np
from pyti.relative_strength_index import relative_strength_index as rsi
from pyti.simple_moving_average import simple_moving_average as sma
from pyti.moving_average_convergence_divergence import (
    moving_average_convergence_divergence as macd,
)
from core.models import HistoricalData
import logging

logging.basicConfig(
    filename="volatility.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def calculate_volatility(pair_name, period=None):
    try:
        historical_data = HistoricalData.objects.filter(pair__name=pair_name).order_by(
            "-date"
        )

        if period:
            historical_data = historical_data[:period]

        prices = [float(data.close_price) for data in historical_data]

        if len(prices) < 2:
            return None

        results = {}
        periods = [period] if period else [30, 90, 180, 365]
        for p in periods:
            if len(prices) >= p:
                period_prices = prices[:p]
                returns = np.diff(np.log(period_prices))
                volatility = np.std(returns)
                results[f"volatility_{p}_days"] = round(volatility, 4)
            else:
                results[f"volatility_{p}_days"] = None

        return results
    except Exception as e:
        logging.error(f"Ошибка при расчёте волатильности для {pair_name}: {e}")
        return None


def calculate_technical_indicators(pair_name):
    try:
        historical_data = HistoricalData.objects.filter(pair__name=pair_name).order_by(
            "-date"
        )

        prices = [float(data.close_price) for data in historical_data[:200]]

        if len(prices) < 30:
            return None

        indicators = {
            "rsi_14": rsi(prices[-14:], 14)[-1] if len(prices) >= 14 else None,
            "sma_50": sma(prices[-50:], 50)[-1] if len(prices) >= 50 else None,
            "sma_200": sma(prices, 200)[-1] if len(prices) >= 200 else None,
            "macd": macd(prices, 12, 26)[-1] if len(prices) >= 26 else None,
        }

        for key in indicators:
            if indicators[key] is not None:
                indicators[key] = round(indicators[key], 4)

        return indicators
    except Exception as e:
        logging.error(f"Ошибка при расчёте индикаторов для {pair_name}: {e}")
        return None


def generate_strategy(amount, risk_level, indicators=None):
    try:
        allocation = 0
        risk_allocations = {"low": 0.2, "medium": 0.5, "high": 0.8}

        if risk_level in risk_allocations:
            allocation = amount * risk_allocations[risk_level]
        else:
            raise ValueError(f"Неверный уровень риска: {risk_level}")

        strategy = {
            "risk_level": risk_level,
            "total_investment": round(amount, 2),
            "allocated_amount": round(allocation, 2),
        }

        if indicators:
            strategy["indicators"] = indicators

        return strategy
    except Exception as e:
        logging.error(f"Ошибка при генерации стратегии: {e}")
        return None
