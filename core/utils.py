import pandas as pd
import numpy as np
import talib


def calculate_volatility(pair_name):
    from core.models import HistoricalData

    historical_data = HistoricalData.objects.filter(pair__name=pair_name).order_by(
        "date"
    )
    if not historical_data.exists():
        return None

    df = pd.DataFrame(list(historical_data.values("date", "close_price")))
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    df["log_return"] = np.log(df["close_price"] / df["close_price"].shift(1))

    volatility = {
        "30d_volatility": df["log_return"].rolling(window=30).std().iloc[-1],
        "90d_volatility": df["log_return"].rolling(window=90).std().iloc[-1],
        "180d_volatility": df["log_return"].rolling(window=180).std().iloc[-1],
        "365d_volatility": df["log_return"].rolling(window=365).std().iloc[-1],
    }
    return volatility


def calculate_ta_indicators(df):
    close_prices = df["close_price"].values
    df["sma_30"] = talib.SMA(close_prices, timeperiod=30)
    df["ema_30"] = talib.EMA(close_prices, timeperiod=30)
    df["rsi_14"] = talib.RSI(close_prices, timeperiod=14)
    return df


def generate_strategy_for_risk_level(risk_level):
    if risk_level == 1:
        return {
            "name": "Купить и держать",
            "description": "Инвестирование в стабильные пары",
        }
    elif risk_level == 5:
        return {
            "name": "Агрессивная торговля",
            "description": "Частая торговля по волатильным парам",
        }
    else:
        return {
            "name": "Смешанная стратегия",
            "description": f"Стратегия для уровня риска {risk_level}",
        }
