import asyncio
import httpx
import logging
from django.core.management.base import BaseCommand
from core.models import CryptoPair, HistoricalData
from datetime import datetime
from django.utils.timezone import make_aware
from tzlocal import get_localzone
from asgiref.sync import sync_to_async
from tenacity import retry, wait_fixed, stop_after_attempt

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(
    filename="logfile.log", level=logging.INFO, format=LOG_FORMAT, filemode="a"
)
logger = logging.getLogger(__name__)

semaphore = asyncio.Semaphore(5)

class Command(BaseCommand):
    help = "Асинхронная загрузка исторических данных для избранных пар"

    @retry(wait=wait_fixed(2), stop=stop_after_attempt(3))
    async def fetch_historical_data(self, client, pair):
        url = f"https://api.bybit.com/v5/market/kline?category=spot&symbol={pair.name}&interval=1&limit=200"
        async with semaphore:
            try:
                logger.info(f"Запрос исторических данных для пары: {pair.name}")
                response = await client.get(url, timeout=30)
                response.raise_for_status()
                data = response.json()

                if "result" in data and "list" in data["result"] and data["result"]["list"]:
                    historical_data = data["result"]["list"]

                    for record in historical_data:
                        date_naive = datetime.fromtimestamp(int(record[0]) / 1000)
                        date_aware = make_aware(date_naive, timezone=get_localzone())

                        await sync_to_async(HistoricalData.objects.update_or_create)(
                            pair=pair,
                            date=date_aware,
                            defaults={
                                "open_price": float(record[1]),
                                "close_price": float(record[2]),
                                "high_price": float(record[3]),
                                "low_price": float(record[4]),
                                "volume": float(record[5]),
                            },
                        )
                    logger.info(f"Исторические данные для пары {pair.name} успешно обновлены.")
                else:
                    logger.warning(f"Нет данных для пары {pair.name} или данные пусты.")

            except httpx.RequestError as e:
                logger.error(f"Ошибка сети при запросе данных для {pair.name}: {e}")
            except Exception as e:
                logger.error(f"Ошибка при обработке данных для {pair.name}: {e}", exc_info=True)

    async def handle_async(self):
        pairs = await sync_to_async(list)(CryptoPair.objects.all())
        if not pairs:
            logger.warning("Нет доступных пар для анализа.")
            self.stderr.write("Нет доступных пар для анализа.")
            return

        async with httpx.AsyncClient() as client:
            tasks = [self.fetch_historical_data(client, pair) for pair in pairs]
            await asyncio.gather(*tasks)

        logger.info("=== Завершение загрузки исторических данных ===")

    def handle(self, *args, **kwargs):
        logger.info("=== Старт асинхронной загрузки исторических данных ===")
        asyncio.run(self.handle_async())
