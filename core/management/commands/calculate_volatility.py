from django.core.management.base import BaseCommand
from core.analytics import calculate_volatility


class Command(BaseCommand):
    help = "Рассчитывает волатильность для криптопары"

    def add_arguments(self, parser):
        parser.add_argument(
            "pair_name", type=str, help="Название криптопары (например, BTCUSDT)"
        )
        parser.add_argument(
            "--period", type=int, help="Период (например, 30, 90, 180 или 365 дней)"
        )

    def handle(self, *args, **kwargs):
        pair_name = kwargs["pair_name"]
        period = kwargs.get("period")
        try:
            volatility = calculate_volatility(pair_name, period=period)
            if volatility is not None:
                self.stdout.write(
                    self.style.SUCCESS(f"Волатильность для {pair_name}: {volatility}")
                )
            else:
                self.stderr.write(
                    self.style.ERROR(
                        f"Не удалось рассчитать волатильность для {pair_name}"
                    )
                )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"Ошибка при расчёте волатильности: {e}")
            )
