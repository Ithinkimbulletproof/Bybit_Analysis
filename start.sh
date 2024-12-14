#!/bin/bash

# 1. Запуск Redis-сервера
echo "🔄 Запуск Redis-сервера..."
sudo service redis-server start

echo "✅ Redis запущен."

# 2. Активация виртуального окружения
echo "🔄 Активация виртуального окружения..."
source ../.venv/bin/activate  # Изменено на правильный путь

echo "✅ Виртуальное окружение активировано."

# 3. Запуск Django-сервера
echo "🔄 Запуск Django-сервера..."
python manage.py runserver 0.0.0.0:8000 &

echo "✅ Django-сервер запущен на http://127.0.0.1:8000"

# 4. Запуск Celery воркера от обычного пользователя
echo "🔄 Запуск Celery воркера..."
# Запускаем Celery от обычного пользователя (замените your_user_name на нужное имя)
sudo -u your_user_name celery -A bybit_analysis.celery worker --loglevel=info --pool=prefork &

echo "✅ Celery запущен."

