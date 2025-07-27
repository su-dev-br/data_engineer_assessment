import json 
import os
import pandas as pd

from mysqlConnector import MySQLConnection
from utils import *


def load_json_data(json_data, ms: MySQLConnection):

    # convert JSON data to DataFrame
    df = json_df(json_data)

    #   flatten nested data structures
    df = flatten_data(df)

    #   generate MD5 hash for the 'primary keys' column
    print("Generating MD5 hash for primary keys...", df.shape)
    prime_df = df['Property_Title'].astype(str)
    df['md5_id'] = prime_df.apply(generate_md5_hash)
    print("Dataframe shape:", df.shape)

    ms.merge_into_mysql(df, 'property_info')
    print("Data loaded into MySQL successfully.")


def main():

    ROOT_PATH, MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE = get_db_config()
    ms = MySQLConnection(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)
    
    json_file_path = os.path.join(ROOT_PATH, "data", "fake_property_data.json")
    json_data = read_json(json_file_path)

    print("Loading JSON data into MySQL...")
    load_json_data(json_data, ms)



    print("Data loaded successfully into MySQL.")
    ms.close_connection()

    #call 6 function parllelly
    # from scripts.etl_1 import main as etl_1_main
    # from scripts.etl_3 import main as etl_3_main
    # from scripts.etl_4 import main as etl_4_main
    # from scripts.etl_5 import main as etl_5_main
    # from scripts.etl_6 import main as etl_6_main
    # from scripts.etl_7 import main as etl_7_main
    # from multiprocessing import Pool
    # with Pool(processes=6) as pool:
    #     pool.map(lambda f: f(), [etl_1_main, etl_3_main, etl_4_main, etl_5_main, etl_6_main, etl_7_main])     



if __name__ == "__main__":

    main()
   