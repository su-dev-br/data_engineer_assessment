import json 
import os
import pandas as pd

from mysqlConnector import MySQLConnection
from utils import fetch_table_metadata, write_to_mysql, update_df_dtypes, read_json, get_db_config



pd.options.display.max_columns = 5
pd.options.display.max_rows = 10

ROOT_PATH = os.getcwd()
print("ROOT_PATH:", ROOT_PATH)


# def write_to_mysql(df, table_name, connection):
#     cursor = connection.cursor()
#     for index, row in df.iterrows():
#         sql = f"INSERT INTO {table_name} (column1, column2) VALUES (%s, %s)"
#         cursor.execute(sql, tuple(row))
#     connection.commit()
#     cursor.close()
#     print(f"Data written to {table_name} table successfully.")


# def load_data(data, schema):
#     df = pd.DataFrame(data)
#     for table_name, columns in schema.items():
#         list_columns = columns.keys()
#         columns_dtypes = {col: dt for col, dt in columns.items() if col in list_columns}

#         df = df[list_columns].astype(columns_dtypes)
#         df.head(5)

#         print(f"Loading data into table: {table_name} with columns: {list_columns} and datatypes: {columns_dtypes}")

def get_column_mapping(items): 
    dtypes = {}
    for key, val in items.items():
        if val['type'] == 'string':
            dtypes[key] = 'VARCHAR(255)'
        elif val['type'] == 'integer':
            dtypes[key] = 'INT'
        elif val['type'] == 'float':
            dtypes[key] = 'FLOAT'   

    print("Column Data Types Mapping:", dtypes)
    return dtypes     

def get_table_df(df , mapping):
    select_list = mapping['select_list']
    json_column = mapping.get('json_list')
    arr_column = mapping.get('arr_column')
    print(f"Processing mapping with select_list: {select_list} and arr_column: {arr_column}")
    df = df[select_list]
    if mapping['type'] == 'array' or arr_column is not None:
        if arr_column != []:
            for col in arr_column:
                df = df.explode([col])
        if json_column != []:
            for col in json_column:
                df = pd.json_normalize(df[col])
    df = df.fillna('')  # Fill NaN values with empty strings
    print(f"DataFrame", df.dtypes)
    return df


if __name__ == "__main__":

    ROOT_PATH, MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE = get_db_config()
    ms = MySQLConnection(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)

    
    json_file_path = os.path.join(ROOT_PATH, "data", "fake_property_data.json")
    json_data = read_json(json_file_path)
    
    schema_file_path = os.path.join(ROOT_PATH, "schema", "schemas.json")
    schema_data = read_json(schema_file_path)

    dtypes_file_path = os.path.join(ROOT_PATH, "schema", "datatypes.json")
    datatypes = read_json(dtypes_file_path)['mysql']
    
    df = pd.DataFrame(json_data)
    conn = ms.connect_to_mysql()
    print("Connection established to MySQL database.", conn)
    for table_name, items in schema_data.items():
        df = get_table_df(df, items)
        # print(f"DataFrame for {table_name}:\n", df.head(5))
        metadata = fetch_table_metadata(connection=conn, table_name=table_name)
        # df = update_df_dtypes(df, metadata, datatypes)

        write_to_mysql(df, table_name, ms.connect_to_mysql())
    
    # load_data(json_data, schema_data)

    # print("JSON Data:", type(json_data))
    # print("JSON Data:", json_data[0]['Valuation'][0]['Previous_Rent'])

    # df = pd.DataFrame(json_data)
    # # print("DataFrame:\n", df.dtypes)
    # # print("DataFrame Columns:", df.columns)
    # # print(df[['Property_Title', 'Valuation']].head(5))

    # df = df['Valuation'].apply(lambda x:x[0]).head(5).to_string(header=True, index=False)



    # pd.options.display.width = 1000
    # df = pd.read_table(StringIO(df), sep="\s+", header=0, index_col=False)

    # print(tabulate(df, headers='keys', tablefmt='psql'))


    # if ms.test_connection():
    #     print("Connection test passed")

    #     connection = ms.connect_to_mysql()
    #     write_to_mysql(df, 'property_data', connection)
    #     connection.close()
    # else:
    #     print("Failed to connect to MySQL Server.")