import numpy as np
from core.models import HistoricalData


def calculate_volatility(pair_name):
    try:
        historical_data = HistoricalData.objects.filter(pair__name=pair_name).order_by(
            "date"
        )
        prices = [float(data.close_price) for data in historical_data]

        if len(prices) < 2:
            return None

        returns = np.diff(np.log(prices))
        volatility = np.std(returns)
        return round(volatility, 4)
    except Exception as e:
        print(f"Ошибка при расчёте волатильности для {pair_name}: {e}")
        return None


def generate_strategy(amount, risk_level):
    allocation = 0

    risk_allocations = {"low": 0.2, "medium": 0.5, "high": 0.8}

    if risk_level in risk_allocations:
        allocation = amount * risk_allocations[risk_level]
    else:
        raise ValueError(f"Неверный уровень риска: {risk_level}")

    return {
        "risk_level": risk_level,
        "total_investment": round(amount, 2),
        "allocated_amount": round(allocation, 2),
    }
