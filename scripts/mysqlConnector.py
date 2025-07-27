from typing import Optional, List, Any
import mysql.connector as ms
import pandas as pd


class MySQLConnection:
    """
    Context-managed MySQL connection handler with utility methods for executing queries,
    syncing DataFrame columns to MySQL, loading DataFrames to tables, and metadata fetching.
    Ensures minimal connection overhead by reusing the same connection and cursor per instance.
    """

    def __init__(
        self,
        user: str,
        password: str,
        host: str = 'localhost',
        port: int = 3306,
        database: Optional[str] = None
    ):
        """
        Initialize MySQLConnection with credentials and connection params.

        :param user: MySQL username
        :param password: MySQL password
        :param host: MySQL host address (default: localhost)
        :param port: MySQL port (default: 3306)
        :param database: Initial database to connect to (optional)
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

        self.connection: Optional[ms.MySQLConnection] = None
        self.cursor: Optional[ms.cursor.MySQLCursorDict] = None

    def connect(self) -> ms.MySQLConnection:
        """
        Establish a connection to the MySQL server if not already connected.

        :return: Active MySQL connection instance
        :raises RuntimeError: If connection fails
        """
        if self.connection and self.connection.is_connected():
            return self.connection

        try:
            self.connection = ms.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                return self.connection
            else:
                raise RuntimeError("Failed to establish connection to MySQL server")
        except ms.Error as err:
            raise RuntimeError(f"MySQL connection error: {err}") from err

    def get_cursor(self, buffered: bool = True, dictionary: bool = True) -> ms.cursor.MySQLCursorDict:
        """
        Get a cursor from the active connection. Caches the cursor to reuse.

        :param buffered: Whether the cursor should be buffered (default: True)
        :param dictionary: Return rows as dicts if True, tuples if False (default: True)
        :return: MySQL cursor instance
        :raises RuntimeError: If connection not active
        """
        if not self.connection or not self.connection.is_connected():
            self.connect()

        if self.cursor and not self.cursor.close:
            return self.cursor

        self.cursor = self.connection.cursor(buffered=buffered, dictionary=dictionary)
        return self.cursor

    def close_cursor(self) -> None:
        """
        Close the current cursor if open.
        """
        if self.cursor and not self.cursor.close:
            self.cursor.close()
        self.cursor = None

    def close(self) -> None:
        """
        Close cursor and connection gracefully.
        """
        self.close_cursor()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None

    def test_connection(self) -> bool:
        """
        Test the connection by executing a simple query.

        :return: True if query successful, False otherwise
        """
        try:
            cursor = self.get_cursor(dictionary=False)
            cursor.execute("SELECT 1 + 1;")
            result = cursor.fetchone()
            self.close_cursor()
            return result is not None
        except ms.Error:
            return False

    def execute_sql_query(self, query: str) -> List[dict]:
        """
        Execute a SQL query and fetch all results.

        :param query: SQL query string
        :return: List of result rows (dicts)
        :raises RuntimeError: If execution fails
        """
        try:
            cursor = self.get_cursor()
            print(f"Executing SQL query: {query}")
            cursor.execute(query)
            results = cursor.fetchall()
            print(f"Query executed successfully, fetched {len(results)} rows.")
            self.close_cursor()
            return results
        except ms.Error as err:
            self.close_cursor()
            raise RuntimeError(f"SQL query error: {err}") from err

    def execute_sql_file(self, file_path: str) -> None:
        """
        Execute all SQL statements in a file sequentially.

        :param file_path: Path to the .sql file
        :raises RuntimeError: If execution fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                sql_commands = file.read()

            cursor = self.get_cursor(dictionary=False)
            for command in sql_commands.split(';'):
                command = command.strip()
                if command:
                    cursor.execute(command)
            self.connection.commit()
            self.close_cursor()
        except ms.Error as err:
            self.connection.rollback()
            self.close_cursor()
            raise RuntimeError(f"Failed to execute SQL file '{file_path}': {err}") from err

    def fetch_table_metadata(self, table_name: str, database: Optional[str] = None) -> List[dict]:
        """
        Retrieve column metadata for a given table.

        :param table_name: Table name
        :param database: Database name to qualify table (optional)
        :return: List of column metadata dicts
        """
        qualified_table = f"`{database}`.`{table_name}`" if database else f"`{table_name}`"
        query = f"DESCRIBE {qualified_table}"
        print(f"Fetching metadata for table '{table_name}' in database '{database}'...")
        return self.execute_sql_query(query)

    def get_primary_keys(self, table_name: str) -> List[str]:
        """
        Get the primary key column names for the specified table.

        :param table_name: Table to check
        :return: List of primary key columns
        """
        query = f"SHOW KEYS FROM `{table_name}` WHERE Key_name='PRIMARY'"
        results = self.execute_sql_query(query)
        # The column name is in the 'Column_name' key when dictionary=True
        pk_cols = [row['Column_name'] for row in results] if results else []
        print(f"Primary keys for table '{table_name}': {pk_cols}")
        return pk_cols

    def sync_columns_with_mysql(self, df, table_name: str) -> None:
        """
        Add missing columns from pandas DataFrame into the MySQL table.

        :param df: pandas DataFrame with data
        :param table_name: MySQL table name
        """
        print(f"Syncing DataFrame columns with MySQL table '{table_name}'...")
        cursor = self.get_cursor(dictionary=False)
        cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
        existing_cols = set(row[0] for row in cursor.fetchall())

        new_cols = set(df.columns) - existing_cols

        for col in new_cols:
            dtype = df[col].dtype

            if pd.api.types.is_integer_dtype(dtype):
                sql_type = 'INT'
            elif pd.api.types.is_float_dtype(dtype):
                sql_type = 'FLOAT'
            elif pd.api.types.is_bool_dtype(dtype):
                sql_type = 'BOOLEAN'
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                sql_type = 'DATETIME'
            else:
                # Default to TEXT for object or any other unknown dtype
                sql_type = 'TEXT'

            alter_stmt = f"ALTER TABLE `{table_name}` ADD COLUMN `{col}` {sql_type}"
            print(f"Adding new column to MySQL: {alter_stmt}")
            cursor.execute(alter_stmt)

        self.connection.commit()
        self.cursor.close()

    def df_to_sql(self, df, table_name: str) -> None:
        """
        Bulk insert data from pandas DataFrame into MySQL table.

        :param df: pandas DataFrame with data
        :param table_name: Target MySQL table name
        """
        print(f"Inserting DataFrame into MySQL table '{table_name}'...")
        cursor = self.get_cursor(dictionary=False)
        cols = list(df.columns)
        placeholders = ', '.join(['%s'] * len(cols))
        columns_str = ', '.join([f"`{col}`" for col in cols])
        sql = f"INSERT INTO `{table_name}` ({columns_str}) VALUES ({placeholders})"

        data = [tuple(row) for row in df.itertuples(index=False, name=None)]
        cursor.executemany(sql, data)
        self.connection.commit()
        self.close_cursor()

  
    
    def merge_into_mysql(self, df, table_name: str) -> None:
        """
        Sync columns and insert DataFrame data into the MySQL table, handling primary keys.

        :param df: pandas DataFrame to insert
        :param table_name: Target MySQL table name
        """
        print(f"Merging DataFrame into MySQL table '{table_name}' based on primary keys...")
        self.sync_columns_with_mysql(df, table_name)
        cursor = self.get_cursor(dictionary=False)
        
        pk_cols = self.get_primary_keys(table_name)
        if not pk_cols:
            raise RuntimeError(f"No primary key found for table '{table_name}'")

        # Prepare SQL for merging data based on primary keys
        cols = list(df.columns)
        placeholders = ', '.join(['%s'] * len(cols))
        update_clause = ', '.join([f"`{col}` = VALUES(`{col}`)" for col in cols if col not in pk_cols])
        
        sql = f"""
            INSERT INTO `{table_name}` ({', '.join([f'`{col}`' for col in cols])})
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {update_clause}
        """

        data = [tuple(row) for row in df.itertuples(index=False, name=None)]
        cursor.executemany(sql, data)
        self.connection.commit()
        self.close_cursor()


    
    def fetch_all(self, query, params=None):
        """Fetch all records from the database."""
        "select id as pi_id, hoa from home_db.property_info"
        cursor = self.get_cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def fetch_one(self, query, params=None):
        """Fetch a single record from the database."""
        cursor = self.get_cursor()
        cursor.execute(query, params)
        return cursor.fetchone()

    # Context manager interface

    def __enter__(self) -> ms.MySQLConnection:
        """
        Support with-statement context entry. Connect on enter.

        :return: MySQL connection instance
        """
        self.connect()
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Support with-statement context exit. Ensure cleanup.

        :param exc_type: Exception type
        :param exc_val: Exception value
        :param exc_tb: Traceback
        """
        self.close()
