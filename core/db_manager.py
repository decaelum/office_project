import sqlite3
from typing import List, Tuple, Any
from core.log_manager import log_message

DATABASE_DIR = ""

class DatabaseManager:
    """
    Context manager-enabled SQLite Database Manager for handling basic operations.
    Usage:
        with DatabaseManager("products.db") as db:
            db.insert_record(...)
    """

    def __init__(self, db_name: str):
        self.db_path = f"{DATABASE_DIR}{db_name}"
        self.connection = None
        self.cursor = None

    def __enter__(self):
        """Opens the database connection when entering the context."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            log_message(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            log_message(f"Database connection error: {e}", level="error")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Ensures the connection is closed when exiting the context."""
        if self.connection:
            self.connection.close()
            log_message("Database connection closed.")

    def execute_query(self, query: str, params: Tuple = ()) -> None:
        """Executes INSERT, UPDATE, DELETE queries."""
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            log_message(f"Query executed successfully: {query}")
        except sqlite3.Error as e:
            log_message(f"Error executing query: {e}", level="error")

    def fetch_query(self, query: str, params: Tuple = ()) -> List[Tuple[Any]]:
        """Executes SELECT queries and returns results."""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            log_message(f"Error fetching query: {e}", level="error")
            return []

    def insert_record(self, table: str, columns: List[str], values: List[Any]) -> None:
        """Inserts a new record into the specified table."""
        placeholders = ", ".join(["?"] * len(values))
        columns_str = ", ".join(columns)
        query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
        self.execute_query(query, tuple(values))

    def update_record(self, table: str, update_fields: dict, condition: str, condition_values: Tuple) -> None:
        """Updates records based on a condition."""
        set_clause = ", ".join([f"{key} = ?" for key in update_fields.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        values = tuple(update_fields.values()) + condition_values
        self.execute_query(query, values)

    def delete_record(self, table: str, condition: str, condition_values: Tuple) -> None:
        """Deletes records based on a condition."""
        query = f"DELETE FROM {table} WHERE {condition}"
        self.execute_query(query, condition_values)
    
    def update_url_by_barcode(self, barcode: str, new_url: str) -> None:
        """
        Updates the URL of a product based on its barcode.

        Args:
        barcode (str): The barcode of the product to update.
        new_url (str): The new URL to set for the product.
        """
        query = "UPDATE products SET url = ? WHERE barcode = ?"
        try:
            self.cursor.execute(query, (new_url, barcode))
            self.connection.commit()
            log_message(f"✅ URL updated for barcode {barcode}.")
        except Exception as e:
            log_message(f"❌ Failed to update URL for barcode {barcode}: {e}", level="error")