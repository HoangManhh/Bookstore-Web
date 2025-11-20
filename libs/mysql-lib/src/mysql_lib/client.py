import mysql.connector
from mysql.connector import Error
from typing import Optional, List, Dict, Any, Tuple

class MySQLClient:
    def __init__(self, host: str = "localhost", user: str = "root", password: str = "pass", database: str = "bookstore_db", port: int = 3306):
        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
            "port": port
        }
        self.connection = None

    def connect(self):
        """Establishes a connection to the database."""
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connection = mysql.connector.connect(**self.config)
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            raise

    def close(self):
        """Closes the database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def execute_query(self, query: str, params: Tuple = None) -> Optional[int]:
        """Executes a query (INSERT, UPDATE, DELETE) and returns the last row id or rowcount."""
        cursor = None
        try:
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.lastrowid if query.strip().upper().startswith("INSERT") else cursor.rowcount
        except Error as e:
            print(f"Error executing query: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def fetch_query(self, query: str, params: Tuple = None, dictionary: bool = True) -> List[Any]:
        """Executes a SELECT query and returns the results."""
        cursor = None
        try:
            self.connect()
            cursor = self.connection.cursor(dictionary=dictionary)
            cursor.execute(query, params)
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching data: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def fetch_one(self, query: str, params: Tuple = None, dictionary: bool = True) -> Optional[Any]:
        """Executes a SELECT query and returns a single result."""
        cursor = None
        try:
            self.connect()
            cursor = self.connection.cursor(dictionary=dictionary)
            cursor.execute(query, params)
            return cursor.fetchone()
        except Error as e:
            print(f"Error fetching data: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
