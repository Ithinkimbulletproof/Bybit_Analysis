from django.core.management.base import BaseCommand
from core.tasks import update_historical_data


class Command(BaseCommand):
    help = "Обновление исторических данных"

    def handle(self, *args, **kwargs):
        update_historical_data.delay()
        self.stdout.write(self.style.SUCCESS("Запущено обновление исторических данных"))
