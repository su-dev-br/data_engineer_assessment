from mysql import connector as ms

class MySQLConnection:
    def __init__(self, user, password, host='localhost', port=3306, database=None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def connect_to_mysql(self):
        try:
            self.connection = ms.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Connected to MySQL Server")
                
                return self.connection
        except ms.Error as err:
            print(f"Error: {err}")
            self.connection = None
            return None
        
    def get_cursor(self, connection):
        if self.connection and self.connection.is_connected():
            self.cursor = self.connection.cursor(dictionary=True)
            return self.cursor
        else:
            print("No active connection to get cursor.")
            return None

    def test_connection(self):
        """Simple query to test connection"""
        if not self.connection or not self.connection.is_connected():
            print("No active connection, trying to connect...")
            con = self.connect_to_mysql()
            if not con:
                return False

        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1 + 1;")
            result = cursor.fetchone()
            cursor.close()
            print("Test query result:", result)
            return True
        except ms.Error as err:
            print(f"Test query failed: {err}")
            return False
    
    def get_primary_keys(self, connection, table_name):
        cursor = connection.cursor()
        cursor.execute(f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY'")
        pk_cols = [row[4] for row in cursor.fetchall()]
        cursor.close()
        return pk_cols

    def execute_sql_query(self, query, cursor):
        print(f"Executing SQL query: {query}")
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result

    def execute_sql_file(self, file_path, connection):
        with open(file_path, 'r') as file:
            sql_commands = file.read().split(';')  # Split commands by semicolon
        cursor = connection.cursor()
        for command in sql_commands:
            command = command.strip()
            self.execute_sql_query(command, cursor)
        connection.commit()
        cursor.close()
        print(f"Executed SQL commands from {file_path} successfully.")

    
    def fetch_table_metadata(self, connection, table_name, database=None):
        cursor = connection.cursor()
        # If database specified, qualify table name
        qualified_table = f"`{database}`.`{table_name}`" if database else table_name
        cursor.execute(f"DESCRIBE {qualified_table}")
        columns = cursor.fetchall()  # List of dicts with keys: Field, Type, Null, Key, Default, Extra
        cursor.close()
        return columns
    
    def df_to_sql(self, df, table_name, connection):
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
    
    def sync_columns_with_mysql(self, df, table_name, connection):
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
            elif dtype == 'object':
                sql_type = 'TEXT'
            else:
                sql_type = 'VARCHAR(255)'
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN `{col}` {sql_type}")
        connection.commit()
        cursor.close()

    def merge_into_mysql(self, df, table_name, connection):
        self.sync_columns_with_mysql(df, table_name, connection)
        self.df_to_sql(df, table_name, connection)

    # Context manager methods
    def __enter__(self):
        print("Establishing MySQL connection...")
        if not self.connection or not self.connection.is_connected():
            connection = self.connect_to_mysql()
            if connection is None:
                raise RuntimeError("Failed to connect to MySQL")
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed.")
