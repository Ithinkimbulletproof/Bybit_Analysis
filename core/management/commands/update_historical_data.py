from django.core.management.base import BaseCommand
from core.tasks import update_historical_data
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Обновление исторических данных"

    def handle(self, *args, **kwargs):
        try:
            logger.info("Запуск обновления исторических данных")
            update_historical_data.delay()
            self.stdout.write(
                self.style.SUCCESS("Запущено обновление исторических данных")
            )
            logger.info("Обновление исторических данных успешно запущено")
        except Exception as e:
            logger.error(f"Ошибка при запуске обновления исторических данных: {e}")
            self.stderr.write(self.style.ERROR(f"Ошибка при запуске обновления: {e}"))
