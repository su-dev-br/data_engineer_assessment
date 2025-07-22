#! bin/bash

source pyenv/bin/activate


export ROOT_PATH = pwd
export MYSQL_HOST=localhost
export MYSQL_USER=db_user
export MYSQL_DATABASE=home_db
export MYSQL_PASSWORD=6equj5_db_user

python3 ./scripts/etl_1.py



