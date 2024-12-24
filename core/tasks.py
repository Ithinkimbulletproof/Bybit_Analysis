import httpx
import logging
from celery import shared_task
from core.models import CryptoPair, HistoricalData
from core.analytics import calculate_technical_indicators
from datetime import datetime
from django.utils.timezone import make_aware
from tzlocal import get_localzone

logger = logging.getLogger(__name__)


@shared_task
def update_crypto_predictions():
    logger.info("Запуск обновления прогнозов для криптовалютных пар.")
    pairs = CryptoPair.objects.all()
    for pair in pairs:
        indicators = calculate_technical_indicators(pair.name)
        if indicators:
            pair.growth_prediction = indicators.get("prediction")
            pair.save()
            logger.info(
                f"Прогноз обновлен для пары {pair.name}: {pair.growth_prediction}"
            )


@shared_task
def update_historical_data():
    pairs = CryptoPair.objects.all()
    logger.info(
        f"Обрабатываем {len(pairs)} криптовалютных пар для обновления исторических данных."
    )
    for pair in pairs:
        logger.info(f"Запрашиваем данные для пары {pair.name}.")
        fetch_historical_data.delay(pair.name)


@shared_task
def fetch_historical_data(pair_name):
    url = f"https://api.bybit.com/v5/market/kline?category=spot&symbol={pair_name}&interval=1&limit=200"
    logger.info(f"Отправляем запрос на API для пары {pair_name}: {url}")

    try:
        response = httpx.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        logger.info(f"Ответ от API для {pair_name}: {data}")

        if "result" in data and "list" in data["result"]:
            historical_data = data["result"]["list"]
            logger.info(f"Получено {len(historical_data)} записей для {pair_name}")

            if not historical_data:
                logger.warning(f"Нет данных для {pair_name}")
                return

            growing_pairs = [
                record
                for record in historical_data
                if float(record[2]) > float(record[1])
            ]
            falling_pairs = [
                record
                for record in historical_data
                if float(record[2]) < float(record[1])
            ]

            logger.info(
                f"Для пары {pair_name} найдено {len(growing_pairs)} криптовалют, которые будут расти."
            )
            logger.info(
                f"Для пары {pair_name} найдено {len(falling_pairs)} криптовалют, которые будут падать."
            )

            for record in historical_data:
                try:
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
                    logger.info(
                        f"Данные для {pair_name} на {date_aware} успешно сохранены."
                    )
                except Exception as e:
                    logger.error(
                        f"Ошибка при сохранении данных для {pair_name} на {record}: {e}"
                    )
        else:
            logger.warning(f"Некорректные данные для {pair_name}: {data}")

    except httpx.RequestError as e:
        logger.error(f"Ошибка сети при запросе данных для {pair_name}: {e}")
    except Exception as e:
        logger.error(f"Ошибка при обработке данных для {pair_name}: {e}")


@shared_task
def fetch_crypto_pairs():
    url = "https://api.bybit.com/v5/market/symbols?category=spot"
    logger.info(f"Отправляем запрос на API для списка криптовалютных пар: {url}")

    try:
        response = httpx.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        logger.info(f"Ответ от API для списка пар: {data}")

        if "result" in data and "list" in data["result"]:
            pairs = data["result"]["list"]
            logger.info(f"Получено {len(pairs)} криптовалютных пар.")
            for pair in pairs:
                CryptoPair.objects.update_or_create(
                    name=pair["symbol"],
                    defaults={
                        "base_currency": pair.get("baseCoin", ""),
                        "quote_currency": pair.get("quoteCoin", ""),
                    },
                )
                logger.info(
                    f"Криптопара {pair['symbol']} обновлена или добавлена в базу."
                )
        else:
            logger.warning(f"Нет данных для криптопар: {data}")
    except httpx.RequestError as e:
        logger.error(f"Ошибка сети при запросе криптопар: {e}")
    except Exception as e:
        logger.error(f"Ошибка при обработке данных криптопар: {e}")
