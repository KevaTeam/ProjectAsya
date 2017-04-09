FROM ubuntu:16.04

MAINTAINER Dmitry Mukovkin mukovkin@yandex.ru

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    nginx \
    supervisor \
    mysql-server \
    mysql-client \
    libmysqld-dev \
    pwgen && rm -rf /var/lib/apt/lists/*

# nginx config
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
COPY docker/nginx.conf /etc/nginx/sites-available/default

# supervisor config
COPY docker/supervisor.conf /etc/supervisor/conf.d/

# mysql config
COPY docker/my.cnf /etc/mysql/

# uWSGI config
COPY docker/uwsgi.ini /app/
COPY docker/uwsgi_params /app/

# Copy initialization scripts
COPY docker/start.sh /app/

VOLUME ["/app/platform"]
EXPOSE 80

CMD ["/bin/bash", "/app/start.sh"]