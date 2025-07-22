#!/bin/bash

docker compose -f docker-compose.initial.yml down

source pyenv/bin/activate || python3 -m venv pyenv && source pyenv/bin/activate
# python3 -m venv pyenv
# source pyenv/bin/activate

export ROOT_PATH = pwd
export MYSQL_HOST=localhost
export MYSQL_USER=db_user
export MYSQL_DATABASE=home_db
export MYSQL_PASSWORD=6equj5_db_user



docker compose -f docker-compose.initial.yml up --build -d
# Wait for the MySQL container to be ready
until docker exec -i $(docker ps -qf "name=mysql") mysqladmin ping -h"$MYSQL_HOST" --silent; do
    echo "Waiting for MySQL to be ready..."
    sleep 5
done


pip3 install -r ./requirements.txt

echo "About to run start_up.py"
chmod +x script.sh
python3 scripts/start_up.py
echo "Finished running start_up.py"