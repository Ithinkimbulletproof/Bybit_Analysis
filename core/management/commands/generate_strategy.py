import logging
from django.core.management.base import BaseCommand
from core.analytics import generate_strategy, calculate_technical_indicators

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Генерация стратегии для вложений"

    def add_arguments(self, parser):
        parser.add_argument(
            "pair_name", type=str, help="Название криптопары (например, BTCUSDT)"
        )
        parser.add_argument("amount", type=float, help="Сумма для вложений")
        parser.add_argument(
            "risk_level",
            type=str,
            choices=["low", "medium", "high"],
            help="Уровень риска (low, medium, high)",
        )

    def handle(self, *args, **kwargs):
        pair_name = kwargs["pair_name"]
        amount = kwargs["amount"]
        risk_level = kwargs["risk_level"]

        logger.info(
            f"Запуск генерации стратегии для {pair_name} с суммой {amount} и уровнем риска {risk_level}"
        )

        try:
            if amount <= 0:
                logger.error(f"Сумма {amount} должна быть положительной")
                self.stderr.write(self.style.ERROR("Сумма должна быть положительной"))
                return

            indicators = calculate_technical_indicators(pair_name)
            if not indicators:
                logger.error(
                    f"Не удалось получить технические индикаторы для {pair_name}"
                )
                self.stderr.write(
                    self.style.ERROR("Не удалось получить технические индикаторы")
                )
                return

            strategy = generate_strategy(amount, risk_level, indicators)
            logger.info(f"Сгенерированная стратегия: {strategy}")
            self.stdout.write(
                self.style.SUCCESS(f"Сгенерированная стратегия: {strategy}")
            )
        except Exception as e:
            logger.error(f"Ошибка при генерации стратегии для {pair_name}: {e}")
            self.stderr.write(self.style.ERROR(f"Ошибка при генерации стратегии: {e}"))
