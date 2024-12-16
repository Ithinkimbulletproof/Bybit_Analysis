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
    filename="logfile_historical.log",
    level=logging.INFO,
    format=LOG_FORMAT,
    filemode="a",
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

                historical_data = data.get("result", {}).get("list", [])
                if not historical_data:
                    logger.warning(f"Нет данных для пары {pair.name} или данные пусты.")
                    return

                for record in historical_data:
                    try:
                        date_naive = datetime.fromtimestamp(int(record[0]) / 1000)
                        date_aware = make_aware(date_naive, timezone=get_localzone())
                        open_price, close_price, high_price, low_price, volume = map(
                            float, record[1:6]
                        )

                        await sync_to_async(HistoricalData.objects.update_or_create)(
                            pair=pair,
                            date=date_aware,
                            defaults={
                                "open_price": open_price,
                                "close_price": close_price,
                                "high_price": high_price,
                                "low_price": low_price,
                                "volume": volume,
                            },
                        )
                    except Exception as e:
                        logger.error(
                            f"Ошибка обработки записи для {pair.name}: {record}, ошибка: {e}"
                        )

                logger.info(
                    f"Исторические данные для пары {pair.name} успешно обновлены."
                )
            except httpx.RequestError as e:
                logger.error(f"Ошибка сети при запросе данных для {pair.name}: {e}")
            except Exception as e:
                logger.error(
                    f"Ошибка при обработке данных для {pair.name}: {e}", exc_info=True
                )

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
