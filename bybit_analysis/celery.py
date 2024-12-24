import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bybit_analysis.settings")

app = Celery("bybit_analysis")

app.conf.update(
    worker_pool="prefork",
)

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "update-crypto-predictions-every-30-minutes": {
        "task": "core.tasks.update_crypto_predictions",
        "schedule": 1800.0,
    },
}

app.conf.timezone = "UTC"
