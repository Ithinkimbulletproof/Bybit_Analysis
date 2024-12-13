import httpx
import logging
from django.core.management.base import BaseCommand
from core.models import CryptoPair


LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(
    filename="logfile.log",
    level=logging.INFO,
    format=LOG_FORMAT,
    filemode="a"
)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Загружает список всех торговых пар с Bybit API и сохраняет их в базу данных"

    def handle(self, *args, **kwargs):
        logger.info("=== Старт загрузки списка торговых пар ===")
        url = "https://api.bybit.com/v5/market/instruments-info?category=spot"
        self.stdout.write("Запрашиваю список пар...")

        try:
            logger.info(f"Запрос данных по URL: {url}")
            response = httpx.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            logger.debug(f"Ответ от API: {data}")

            if "result" in data and "list" in data["result"]:
                pairs = data["result"]["list"]
                logger.info(f"Найдено {len(pairs)} пар для обновления.")

                for pair in pairs:
                    CryptoPair.objects.update_or_create(
                        name=pair["symbol"],
                        defaults={
                            "base_currency": pair["baseCoin"],
                            "quote_currency": pair["quoteCoin"],
                        },
                    )
                success_message = f"Успешно загружено {len(pairs)} пар."
                logger.info(success_message)
                self.stdout.write(self.style.SUCCESS(success_message))
            else:
                warning_message = "Не удалось найти список пар в ответе API."
                logger.warning(warning_message)
                self.stderr.write(warning_message)

        except httpx.RequestError as e:
            error_message = f"Ошибка сети: {e}"
            logger.error(error_message)
            self.stderr.write(error_message)

        except Exception as e:
            error_message = f"Произошла ошибка: {e}"
            logger.error(error_message, exc_info=True)
            self.stderr.write(error_message)

        logger.info("=== Завершение загрузки списка торговых пар ===")
