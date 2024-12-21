import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bybit_analysis.settings")

app = Celery("bybit_analysis")

app.conf.update(
    worker_pool="solo",
)

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
