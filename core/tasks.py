import httpx
from celery import shared_task
from core.models import CryptoPair, HistoricalData
from datetime import datetime
from django.utils.timezone import make_aware
from tzlocal import get_localzone


@shared_task
def update_historical_data():
    pairs = CryptoPair.objects.all()
    for pair in pairs:
        fetch_historical_data(pair.name)


def fetch_historical_data(pair_name):
    url = f"https://api.bybit.com/v5/market/kline?category=spot&symbol={pair_name}&interval=1&limit=200"
    try:
        response = httpx.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        if "result" in data and "list" in data["result"] and data["result"]["list"]:
            historical_data = data["result"]["list"]

            for record in historical_data:
                date_naive = datetime.fromtimestamp(int(record[0]) / 1000)
                date_aware = make_aware(date_naive, timezone=get_localzone())

                HistoricalData.objects.update_or_create(
                    pair=CryptoPair.objects.get(name=pair_name),
                    date=date_aware,
                    defaults={
                        "open_price": float(record[1]),
                        "close_price": float(record[2]),
                        "high_price": float(record[3]),
                        "low_price": float(record[4]),
                        "volume": float(record[5]),
                    },
                )
    except httpx.RequestError as e:
        print(f"Ошибка сети при запросе данных для {pair_name}: {e}")
    except Exception as e:
        print(f"Ошибка при обработке данных для {pair_name}: {e}")


@shared_task
def fetch_crypto_pairs():
    url = "https://api.bybit.com/v5/market/symbols?category=spot"
    try:
        response = httpx.get(url)
        response.raise_for_status()
        data = response.json()

        if "result" in data and "list" in data["result"]:
            for pair in data["result"]["list"]:
                CryptoPair.objects.update_or_create(name=pair["symbol"])
    except httpx.RequestError as e:
        print(f"Ошибка сети при запросе криптопар: {e}")
    except Exception as e:
        print(f"Ошибка при обработке данных криптопар: {e}")
