#!/bin/bash

docker compose -f docker-compose.initial.yml down

source pyenv/bin/activate || python3 -m venv pyenv && source pyenv/bin/activate
# python3 -m venv pyenv
# source pyenv/bin/activate
pip3 install -r ./requirements.txt





docker compose -f docker-compose.initial.yml up --build -d