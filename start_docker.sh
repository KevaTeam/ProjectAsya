#!/usr/bin/env bash

docker build --rm -t shipko/asya .
docker run -v $(pwd):/app/platform/ -itd -p 80:80 shipko/asya