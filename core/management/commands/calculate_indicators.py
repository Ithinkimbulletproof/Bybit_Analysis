from django.core.management.base import BaseCommand
from core.analytics import calculate_technical_indicators


class Command(BaseCommand):
    help = "Рассчитывает технические индикаторы для криптопары"

    def add_arguments(self, parser):
        parser.add_argument(
            "pair_name", type=str, help="Название криптопары (например, BTCUSDT)"
        )

    def handle(self, *args, **kwargs):
        pair_name = kwargs["pair_name"]
        indicators = calculate_technical_indicators(pair_name)
        if indicators:
            self.stdout.write(
                self.style.SUCCESS(f"Индикаторы для {pair_name}: {indicators}")
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"Не удалось рассчитать индикаторы для {pair_name}")
            )
