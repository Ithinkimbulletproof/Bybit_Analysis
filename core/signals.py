from django.db.models.signals import post_migrate
from django.dispatch import receiver
from core.tasks import update_historical_data


@receiver(post_migrate)
def run_startup_tasks(sender, **kwargs):
    print("Запуск задачи обновления данных...")
    update_historical_data.delay()
    print("Задача обновления данных запущена.")
