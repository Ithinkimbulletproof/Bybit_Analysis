import numpy as np
from core.models import HistoricalData


def calculate_volatility(pair_name):
    try:
        historical_data = HistoricalData.objects.filter(pair__name=pair_name).order_by(
            "date"
        )
        prices = [data.close_price for data in historical_data]

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

    if risk_level == "low":
        allocation = amount * 0.2
    elif risk_level == "medium":
        allocation = amount * 0.5
    elif risk_level == "high":
        allocation = amount * 0.8

    return {
        "risk_level": risk_level,
        "total_investment": amount,
        "allocated_amount": round(allocation, 2),
    }
