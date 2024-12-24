from django.apps import AppConfig
from django.core.management import call_command
import logging
from django.db.models.signals import post_migrate

logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        logger.info("=== Метод ready() запустился ===")
        super().ready()

        post_migrate.connect(self.run_async_task, sender=self)

    def run_async_task(self, **kwargs):
        try:
            from core.analytics import analyze_and_update_trends
            from core.models import HistoricalData, CryptoPair

            logger.info("=== Запуск обновления списка криптопар при старте Django ===")
            call_command("load_pairs")
            logger.info("=== Обновление списка криптопар завершено ===")

            logger.info("=== Запуск анализа криптопар ===")
            analyze_and_update_trends()
            logger.info("=== Анализ криптопар завершен ===")

        except Exception as e:
            logger.error(f"Ошибка при обновлении списка криптопар или анализе: {e}")
