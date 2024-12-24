import logging
from django.core.management.base import BaseCommand
from core.analytics import run_backtrader

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Тестирование стратегий через Backtrader"

    def add_arguments(self, parser):
        parser.add_argument(
            "pair_name", type=str, help="Название криптопары (например, BTCUSDT)"
        )

    def handle(self, *args, **kwargs):
        pair_name = kwargs["pair_name"]

        logger.info(f"Запуск тестирования стратегии для криптопары: {pair_name}")

        try:
            logger.info(f"Запуск стратегии для пары: {pair_name}")
            run_backtrader(pair_name)

            logger.info(f"Тестирование стратегии для {pair_name} завершено")

            self.stdout.write(
                self.style.SUCCESS(f"Тестирование стратегии для {pair_name} завершено")
            )
        except Exception as e:
            logger.error(f"Ошибка при тестировании стратегии для {pair_name}: {e}")

            self.stderr.write(self.style.ERROR(f"Ошибка: {e}"))
