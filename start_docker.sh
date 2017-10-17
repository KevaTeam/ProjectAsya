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
    else
        break
    fi

done

if ! command_exists docker; then
    echo -e "\e[31mIt seems that you have not installed docker. Install it.\e[0m"
    wget -qO- https://get.docker.com/ | sh
fi

echo -e "\e[32mDocker is installed. Run platform.\e[0m"

docker build --rm -t shipko/asya .
docker run -v $(pwd):/app/platform/ -itd -p $port:80 shipko/asya
