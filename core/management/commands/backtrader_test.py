from django.core.management.base import BaseCommand
from core.analytics import run_backtrader


class Command(BaseCommand):
    help = "Тестирование стратегий через Backtrader"

    def add_arguments(self, parser):
        parser.add_argument(
            "pair_name", type=str, help="Название криптопары (например, BTCUSDT)"
        )

    def handle(self, *args, **kwargs):
        pair_name = kwargs["pair_name"]

        try:
            run_backtrader(pair_name)
            self.stdout.write(
                self.style.SUCCESS(f"Тестирование стратегии для {pair_name} завершено")
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ошибка: {e}"))
