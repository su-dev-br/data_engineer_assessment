import os
import pandas as pd

from mysqlConnector import MySQLConnection
from utils import *

# function to create table if it does not exist
def create_tables():
    print("Starting up the application...")
    # Load database configuration
    ROOT_PATH, MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE = get_db_config()

    # Initialize MySQL connection
    ms = MySQLConnection(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)

    sql_file_path = os.path.join(ROOT_PATH,'sql' ,'create_tables.sql')
    print(f"Executing SQL file: {sql_file_path}")
    
    ms.execute_sql_file(sql_file_path)


if __name__ == "__main__":
    create_tables()
    print("Application started successfully.")
