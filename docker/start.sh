#!/bin/bash

SETTING_PATH=`find /app/ -name settings.py`

pip3 install -r /app/requirements.txt

echo "Start mysql server"

mkdir -p /var/run/mysqld
chown mysql:mysql /var/run/mysqld
/usr/bin/mysqld_safe & sleep 5s

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

replace "%DATABASE_PASSWORD%" "$MYSQL_ROOT_PASSWORD" -- /app/docker/docker-django-config.py

cp /app/docker/docker-django-config.py /app/asya/parameters.py

# Django setting
python3 /app/manage.py makemigrations --noinput
python3 /app/manage.py migrate

echo yes | python3 /app/manage.py collectstatic
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', '$DJANGO_ADMIN_PASSWORD')" | python3 /app/manage.py shell

killall mysqld

# Start all the services
/usr/bin/supervisord -n