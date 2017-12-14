#!/bin/bash

pip3 install -r /app/platform/requirements.txt

# Django делает миграции на сервер БД
python3 /app/platform/manage.py makemigrations --noinput
python3 /app/platform/manage.py makemigrations api
python3 /app/platform/manage.py migrate

# Собираем все картинки в одной папке
echo yes | python3 /app/platform/manage.py collectstatic --noinput

# Создаем глобального администратора
# echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', '$DJANGO_ADMIN_PASSWORD')" | python3 /app/platform/manage.py shell

# Запускаем MySQL, nginx, uwsgi
/usr/bin/supervisord -n