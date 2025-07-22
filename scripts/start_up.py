import os
import pandas as pd

from mysqlConnector import MySQLConnection
from utils import get_db_config, execute_sql_file

# function to create table if it does not exist
def create_tables():
    print("Starting up the application...")
    # Load database configuration
    ROOT_PATH, MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE = get_db_config()

    # Initialize MySQL connection
    connection = MySQLConnection(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE).connect_to_mysql()

    sql_file_path = os.path.join(ROOT_PATH,'sql' ,'create_tables.sql')
    print(f"Executing SQL file: {sql_file_path}")
    execute_sql_file(sql_file_path, connection)


if __name__ == "__main__":
    create_tables()
    print("Application started successfully.")
