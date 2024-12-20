import asyncio
import httpx
import logging
from django.core.management.base import BaseCommand
from core.models import CryptoPair
from asgiref.sync import sync_to_async

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(
    filename="logfile.log", level=logging.INFO, format=LOG_FORMAT, filemode="a"
)
logger = logging.getLogger(__name__)


@sync_to_async
def update_or_create_pair(symbol, base_coin, quote_coin):
    CryptoPair.objects.update_or_create(
        name=symbol,
        defaults={
            "base_currency": base_coin,
            "quote_currency": quote_coin,
        },
    )


class Command(BaseCommand):
    help = "Загружает список всех торговых пар с Bybit API и сохраняет их в базу данных"

    async def fetch_pairs(self, client):
        url = "https://api.bybit.com/v5/market/instruments-info?category=spot"
        try:
            response = await client.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "result" in data and "list" in data["result"] and data["result"]["list"]:
                pairs = data["result"]["list"]
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
                            self.stderr.write(
                                self.style.ERROR(
                                    f"Пропуск пары из-за отсутствия ключей: {pair}"
                                )
                            )
                    except Exception as e:
                        self.stderr.write(
                            self.style.ERROR(f"Ошибка при обновлении пары {pair}: {e}")
                        )

            else:
                self.stderr.write(
                    self.style.ERROR(
                        "Ответ API не содержит списка пар или список пуст."
                    )
                )

        except httpx.RequestError as e:
            self.stderr.write(
                self.style.ERROR(f"Ошибка сети при запросе списка пар: {e}")
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ошибка при обработке списка пар: {e}"))

    async def handle_async(self):
        async with httpx.AsyncClient() as client:
            await self.fetch_pairs(client)

    def handle(self, *args, **kwargs):
        logger.info("=== Старт загрузки списка пар ===")
        asyncio.run(self.handle_async())
        logger.info("=== Завершение асинхронной загрузки списка пар ===")
