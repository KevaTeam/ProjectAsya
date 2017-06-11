#!/usr/bin/env bash

command_exists() {
	command -v "$@" > /dev/null 2>&1
}

if ! command_exists docker; then
    echo -e "\e[31mIt seems that you have not installed docker. Install it.\e[0m"
    wget -qO- https://get.docker.com/ | sh
fi

echo -e "\e[32mDocker is installed. Run platform.\e[0m"

docker build --rm -t shipko/asya .
docker run -v $(pwd):/app/platform/ -itd -p 5000:80 shipko/asya
