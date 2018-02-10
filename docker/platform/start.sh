#!/bin/bash

pip3 install -r /app/platform/requirements.txt

cp /app/platform/asya/parameters.py.sample /app/platform/asya/parameters.py

# Django делает миграции на сервер БД
python3 /app/platform/manage.py makemigrations --noinput
python3 /app/platform/manage.py makemigrations api
python3 /app/platform/manage.py migrate

# Собираем все картинки в одной папке
echo yes | python3 /app/platform/manage.py collectstatic --noinput

# Устанавливаем необходимые зависимости
cd /app/platform/frontend/static
curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
sudo apt-get install -y nodejs

npm i

# Создаем глобального администратора
# echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', '$DJANGO_ADMIN_PASSWORD')" | python3 /app/platform/manage.py shell

# Запускаем MySQL, nginx, uwsgi
/usr/bin/supervisord -n