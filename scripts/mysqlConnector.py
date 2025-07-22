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
