from celery import shared_task
import time
import pandas as pd
import numpy as np
from core.models import CryptoPair, HistoricalData, Strategy


@shared_task
def add(x, y):
    time.sleep(5)
    return x + y


@shared_task
def update_crypto_pairs():
    from some_api_client import BybitAPI

    api = BybitAPI()
    pairs = api.get_pairs()

    for pair in pairs:
        CryptoPair.objects.update_or_create(
            name=pair["name"],
            defaults={
                "base_currency": pair["base_currency"],
                "quote_currency": pair["quote_currency"],
            },
        )


@shared_task
def update_historical_data():
    from some_api_client import BybitAPI

    api = BybitAPI()
    pairs = CryptoPair.objects.all()

    for pair in pairs:
        data = api.get_historical_data(pair.name)
        for row in data:
            HistoricalData.objects.update_or_create(
                pair=pair,
                date=row["date"],
                defaults={
                    "open_price": row["open"],
                    "close_price": row["close"],
                    "high_price": row["high"],
                    "low_price": row["low"],
                    "volume": row["volume"],
                },
            )


@shared_task
def generate_strategies():
    risk_levels = range(1, 6)

    for risk in risk_levels:
        expected_return = calculate_expected_return(risk)
        Strategy.objects.update_or_create(
            risk_level=risk,
            defaults={
                "parameters": f"Параметры для уровня риска {risk}",
                "expected_return": expected_return,
            },
        )


@shared_task
def calculate_volatility(pair_name):
    data = HistoricalData.objects.filter(pair__name=pair_name).order_by("date")
    df = pd.DataFrame.from_records(data.values("date", "close_price"))
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    close_prices = df["close_price"].values
    if len(close_prices) < 2:
        return None

    returns = np.diff(close_prices) / close_prices[:-1]
    volatility = np.std(returns)
    return round(volatility, 6)


@shared_task
def calculate_expected_return(risk_level):
    base_return = 5
    expected_return = base_return * risk_level
    return round(expected_return, 2)


@shared_task
def predict_top_10_pairs():
    historical_data = HistoricalData.objects.all()
    df = pd.DataFrame.from_records(
        historical_data.values("pair__name", "date", "close_price")
    )
    df["date"] = pd.to_datetime(df["date"])
    predictions = []

    for pair in df["pair__name"].unique():
        pair_data = df[df["pair__name"] == pair].sort_values("date")
        close_prices = pair_data["close_price"].values

        if len(close_prices) < 2:
            continue

        returns = np.diff(close_prices) / close_prices[:-1]
        vol = np.std(returns)
        trend = "up" if np.mean(returns) > 0 else "down"
        prob = min(1.0, abs(np.mean(returns)) / vol)

        predictions.append(
            {
                "pair": pair,
                "probability": round(prob, 2),
                "expected_change": round(np.mean(returns) * 100, 2),
                "trend": trend,
            }
        )

    sorted_predictions = sorted(
        predictions, key=lambda x: x["probability"], reverse=True
    )[:10]
    return sorted_predictions
