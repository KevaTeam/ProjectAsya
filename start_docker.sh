#!/usr/bin/env bash

command_exists() {
	command -v "$@" > /dev/null 2>&1
}

DEFAULT_PORT=80
echo -e "Let's start to install platform!"
echo -e "Default port [$DEFAULT_PORT]"

while [ true ]
do
    read port

    if [[ "$port" = "" ]] ; then
   	port=$DEFAULT_PORT
    fi

    if sudo netstat -ntul | grep ":$port " > /dev/null; then
        echo "Port $port is already in use"
        echo "Input port: "
    else
        break
    fi
done

if ! command_exists docker; then
    echo -e "\e[31mIt seems that you have not installed docker. Install it.\e[0m"
    wget -qO- https://get.docker.com/ | sh
fi

if ! command_exists docker-compose; then
    echo -e "\e[31mIt seems that you have not installed docker-compose. Install it.\e[0m"
    sudo curl -L https://github.com/docker/compose/releases/download/1.17.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

echo -e "\e[32mDocker, docker-compose is installed. Run platform.\e[0m"

cd docker/

sudo docker-compose up -d --force-recreate