#!/bin/bash

pip3 install -r /app/platform/requirements.txt

echo "Start mysql server"

mkdir -p /var/run/mysqld
chown mysql:mysql /var/run/mysqld
service mysql start

# Set password
MYSQL_ROOT_PASSWORD=`pwgen -c -n -1 12`
MYSQL_DJANGO_PASSWORD=`pwgen -c -n -1 12`
DJANGO_ADMIN_PASSWORD=`pwgen -c -n -1 12`

# Output password
echo -e "MYSQL_ROOT_PASSWORD = $MYSQL_ROOT_PASSWORD\nMYSQL_DJANGO_PASSWORD = $MYSQL_DJANGO_PASSWORD\nDJANGO_ADMIN_PASSWORD = $DJANGO_ADMIN_PASSWORD" > /app/password.txt

# Initialize MySQL
mysqladmin -u root password $MYSQL_ROOT_PASSWORD
mysql -uroot -p$MYSQL_ROOT_PASSWORD -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '$MYSQL_ROOT_PASSWORD' WITH GRANT OPTION; FLUSH PRIVILEGES;"
mysql -uroot -p$MYSQL_ROOT_PASSWORD -e "CREATE DATABASE asya DEFAULT CHARACTER SET utf8; GRANT ALL PRIVILEGES ON asya.* TO 'asya'@'localhost' IDENTIFIED BY '$MYSQL_DJANGO_PASSWORD'; FLUSH PRIVILEGES;"

cp /app/platform/docker/docker-django-config.py /app/platform/asya/parameters.py

replace "%DATABASE_PASSWORD%" "$MYSQL_ROOT_PASSWORD" -- /app/platform/asya/parameters.py


# Django делает миграции на сервер БД
python3 /app/platform/manage.py makemigrations --noinput
python3 /app/platform/manage.py makemigrations api
python3 /app/platform/manage.py migrate

# Собираем все картинки в одной папке
echo yes | python3 /app/platform/manage.py collectstatic --noinput

# Создаем глобального администратора
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', '$DJANGO_ADMIN_PASSWORD')" | python3 /app/platform/manage.py shell

# Останавливаем процессы MySQL
killall mysqld

# Запускаем MySQL, nginx, uwsgi
/usr/bin/supervisord -n
