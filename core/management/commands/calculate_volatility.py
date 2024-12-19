from django.core.management.base import BaseCommand
from core.analytics import calculate_volatility


class Command(BaseCommand):
    help = "Расчёт волатильности для криптопары"

    def add_arguments(self, parser):
        parser.add_argument(
            "pair_name", type=str, help="Название криптопары (например, BTCUSDT)"
        )

    def handle(self, *args, **kwargs):
        pair_name = kwargs["pair_name"]
        volatility = calculate_volatility(pair_name)
        if volatility is not None:
            self.stdout.write(
                self.style.SUCCESS(f"Волатильность для {pair_name}: {volatility}")
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"Не удалось рассчитать волатильность для {pair_name}")
            )
