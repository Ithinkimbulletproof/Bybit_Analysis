import httpx
import logging
from django.core.management.base import BaseCommand
from core.models import CryptoPair, HistoricalData
from datetime import datetime
from django.utils.timezone import make_aware
from tzlocal import get_localzone


LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(
    filename="logfile.log",
    level=logging.INFO,
    format=LOG_FORMAT,
    filemode="a"
)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Загружает исторические данные для избранных пар"

    def handle(self, *args, **kwargs):
        local_timezone = get_localzone()

        pairs = CryptoPair.objects.all()

        if not pairs:
            self.stderr.write("Нет доступных пар для анализа.")
            logger.warning("Нет доступных пар для анализа.")
            return

        self.stdout.write("Запрашиваю исторические данные...")
        logger.info("Запрос исторических данных для пар...")

        for pair in pairs:
            url = f"https://api.bybit.com/v5/market/kline?category=spot&symbol={pair.name}&interval=1&limit=200"

            try:
                response = httpx.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()

                if "result" in data and "list" in data["result"]:
                    historical_data = data["result"]["list"]

                    for record in historical_data:
                        date_naive = datetime.fromtimestamp(int(record[0]) / 1000)
                        date_aware = make_aware(date_naive, timezone=local_timezone)

                        HistoricalData.objects.update_or_create(
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
                    success_message = f"Данные для пары {pair.name} успешно обновлены."
                    logger.info(success_message)
                    self.stdout.write(self.style.SUCCESS(success_message))
                else:
                    warning_message = f"Нет данных для пары {pair.name}."
                    logger.warning(warning_message)
                    self.stderr.write(warning_message)

            except httpx.RequestError as e:
                error_message = f"Ошибка сети при работе с {pair.name}: {e}"
                logger.error(error_message)
                self.stderr.write(error_message)
            except Exception as e:
                error_message = f"Произошла ошибка при работе с {pair.name}: {e}"
                logger.error(error_message, exc_info=True)
                self.stderr.write(error_message)

        logger.info("Завершение загрузки исторических данных.")
