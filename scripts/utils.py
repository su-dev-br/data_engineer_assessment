
import json
import os
import pandas as pd
from dotenv import load_dotenv
from mysqlConnector import MySQLConnection
import hashlib

def get_db_config():
    load_dotenv()
    ROOT_PATH = os.getenv("ROOT_PATH", os.getcwd())
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
    
    return ROOT_PATH, MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE



def read_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def json_df(data):
    df = pd.DataFrame(data)
    return df


def generate_md5_hash(s: str) -> str:
    """Generate MD5 hash for a string."""
    return hashlib.md5(s.encode('utf-8')).hexdigest()

def flatten_data(df):
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, (list, dict))).any():
            df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, (list, dict)) else x)
    return df
            





def update_df_dtypes(df, metadata, datatypes):
    for col_meta in metadata:
        col_name = col_meta['Field']
        raw_type = col_meta['Type']
        # Extract base type (e.g. varchar(255) -> varchar)
        base_type = raw_type.split('(')[0].lower()
        pandas_type = datatypes.get(base_type)
        if pandas_type and col_name in df.columns:
            if pandas_type.startswith('datetime'):
                df[col_name] = pd.to_datetime(df[col_name], errors='coerce')
            else:
                df[col_name] = df[col_name].astype(pandas_type)
    return df



def write_to_mysql(df, table_name, connection):
    cursor = connection.cursor()
    cols = df.columns.tolist()
    placeholders = ', '.join(['%s'] * len(cols))
    columns_str = ', '.join([f"`{col}`" for col in cols])
    sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
    
    # Convert DataFrame rows to list of tuples for execute many
    data = [tuple(row) for row in df.itertuples(index=False, name=None)]
    cursor.executemany(sql, data)
    connection.commit()
    cursor.close()
    print(f"Data loaded into {table_name} successfully.")

def sync_columns_with_mysql(df, table_name, connection):
    cursor = connection.cursor()
    # Get existing columns from MySQL table
    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
    existing_cols = set(row[0] for row in cursor.fetchall())
    # Find new columns in DataFrame
    new_cols = set(df.columns) - existing_cols
    for col in new_cols:
        # Infer type from pandas dtype
        dtype = df[col].dtype
        if dtype == 'int64':
            sql_type = 'INT'
        elif dtype == 'float64':
            sql_type = 'FLOAT'
        elif dtype == 'bool':
            sql_type = 'BOOLEAN'
        else:
            sql_type = 'VARCHAR(255)'
        alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {col} {sql_type}"
        print(f"Adding new column to MySQL: {alter_sql}")
        cursor.execute(alter_sql)
    connection.commit()
    cursor.close()



def merge_into_mysql(df, table_name, connection):
    sync_columns_with_mysql(df, table_name, connection)
    cursor = connection.cursor()
    cols = df.columns.tolist()
    placeholders = ', '.join(['%s'] * len(cols))
    columns_str = ', '.join([f"`{col}`" for col in cols])

    # Get primary key columns
    pk_cols = get_primary_keys(connection, table_name)
    non_pk_cols = [col for col in cols if col not in pk_cols]

    # Create a temporary table
    temp_table_name = f"{table_name}_temp"
    cursor.execute(f"CREATE TEMPORARY TABLE {temp_table_name} ({columns_str})")

    # Insert data into the temporary table
    sql = f"INSERT INTO {temp_table_name} ({columns_str}) VALUES ({placeholders})"
    data = [tuple(row) for row in df.itertuples(index=False, name=None)]
    cursor.executemany(sql, data)

    # Merge data from the temporary table into the main table
    if non_pk_cols:
        update_clause = ', '.join([f"`{col}`=VALUES(`{col}`)" for col in non_pk_cols])
    else:
        update_clause = ''
    merge_sql = f"""
        INSERT INTO {table_name} ({columns_str})
        SELECT {columns_str} FROM {temp_table_name}
        ON DUPLICATE KEY UPDATE {update_clause}
    """
    cursor.execute(merge_sql)

    # Drop the temporary table
    cursor.execute(f"DROP TEMPORARY TABLE {temp_table_name}")

    connection.commit()
    cursor.close()
    print(f"Data merged into {table_name} successfully.")

