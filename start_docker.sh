#!/usr/bin/env bash

docker build --rm -t shipko/asya .
docker run -v /home/dmitry/Projects/asya/:/app/platform/ -itd -p 8081:80 shipko/asya