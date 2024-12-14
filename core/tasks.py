from celery import shared_task
import time

@shared_task
def add(x, y):
    time.sleep(5)
    return x + y

@shared_task
def update_crypto_pairs():
    from django.core.management import call_command
    call_command('load_pairs')

@shared_task
def update_historical_data():
    from django.core.management import call_command
    call_command('load_historical_data')
