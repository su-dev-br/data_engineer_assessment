
import json
import os
from mysqlConnector import MySQLConnection
import pandas as pd

def read_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def fetch_table_metadata(connection, table_name, database=None):
    cursor = connection.cursor(dictionary=True)
    # If database specified, qualify table name
    qualified_table = f"`{database}`.`{table_name}`" if database else table_name
    cursor.execute(f"DESCRIBE {qualified_table}")
    columns = cursor.fetchall()  # List of dicts with keys: Field, Type, Null, Key, Default, Extra
    cursor.close()
    return columns



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