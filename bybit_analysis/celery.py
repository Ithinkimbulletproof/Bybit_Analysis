from celery import Celery
from celery.schedules import crontab

app = Celery("bybit_analysis")

app.conf.beat_schedule = {
    "update-historical-data-every-hour": {
        "task": "core.tasks.update_historical_data",
        "schedule": crontab(minute=0, hour="*"),
    },
    "fetch-crypto-pairs-every-day": {
        "task": "core.tasks.fetch_crypto_pairs",
        "schedule": crontab(minute=0, hour=0),
    },
}
