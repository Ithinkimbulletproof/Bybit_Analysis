import asyncio
import httpx
import logging
from django.core.management.base import BaseCommand
from core.models import CryptoPair
from asgiref.sync import sync_to_async

# Настройка логирования для вывода в консоль
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

logger = logging.getLogger(__name__)


@sync_to_async
def update_or_create_pair(symbol, base_coin, quote_coin):
    try:
        CryptoPair.objects.update_or_create(
            name=symbol,
            defaults={
                "base_currency": base_coin,
                "quote_currency": quote_coin,
            },
        )
        logger.info(f"Обновлена или добавлена пара {symbol}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении пары {symbol}: {e}")


class Command(BaseCommand):
    help = "Загружает список всех торговых пар с Bybit API и сохраняет их в базу данных"

    async def fetch_pairs(self, client):
        url = "https://api.bybit.com/v5/market/instruments-info?category=spot"
        try:
            logger.info("Отправка запроса к API Bybit для получения списка пар")
            response = await client.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "result" in data and "list" in data["result"] and data["result"]["list"]:
                pairs = data["result"]["list"]
                logger.info(f"Получено {len(pairs)} пар с API Bybit")
                for pair in pairs:
                    try:
                        if (
                            "symbol" in pair
                            and "baseCoin" in pair
                            and "quoteCoin" in pair
                        ):
                            await update_or_create_pair(
                                symbol=pair["symbol"],
                                base_coin=pair["baseCoin"],
                                quote_coin=pair["quoteCoin"],
                            )
                        else:
                            logger.warning(
                                f"Пропуск пары из-за отсутствия ключей: {pair}"
                            )
                    except Exception as e:
                        logger.error(f"Ошибка при обновлении пары {pair}: {e}")

            else:
                logger.error("Ответ API не содержит списка пар или список пуст.")

        except httpx.RequestError as e:
            logger.error(f"Ошибка сети при запросе списка пар: {e}")
        except Exception as e:
            logger.error(f"Ошибка при обработке списка пар: {e}")

    async def handle_async(self):
        async with httpx.AsyncClient() as client:
            await self.fetch_pairs(client)

    def handle(self, *args, **kwargs):
        logger.info("=== Старт загрузки списка пар ===")
        asyncio.run(self.handle_async())
        logger.info("=== Завершение асинхронной загрузки списка пар ===")
