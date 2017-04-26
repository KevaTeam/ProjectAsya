#!/usr/bin/env bash

docker build --rm -t shipko/asya .
docker run -v $(pwd):/app/platform/ -itd -p 5000:80 shipko/asya
