from django.core.management.base import BaseCommand
from core.analytics import generate_strategy


class Command(BaseCommand):
    help = "Генерация стратегии для вложений"

    def add_arguments(self, parser):
        parser.add_argument("amount", type=float, help="Сумма для вложений")
        parser.add_argument(
            "risk_level",
            type=str,
            choices=["low", "medium", "high"],
            help="Уровень риска (low, medium, high)",
        )

    def handle(self, *args, **kwargs):
        amount = kwargs["amount"]
        risk_level = kwargs["risk_level"]
        try:
            if amount <= 0:
                self.stderr.write(self.style.ERROR("Сумма должна быть положительной"))
                return
            if risk_level not in ["low", "medium", "high"]:
                self.stderr.write(self.style.ERROR("Недопустимый уровень риска"))
                return

            strategy = generate_strategy(amount, risk_level)
            self.stdout.write(
                self.style.SUCCESS(f"Сгенерированная стратегия: {strategy}")
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ошибка при генерации стратегии: {e}"))
