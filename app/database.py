"""
Database connection module for Trident Energy Risk Manager API
"""

import os
import mysql.connector
from mysql.connector import Error

# Database configuration from environment variables
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "sql7.freesqldatabase.com"),
    "database": os.getenv("DB_NAME", "sql7812701"),
    "user": os.getenv("DB_USER", "sql7812701"),
    "password": os.getenv("DB_PASSWORD", ""),  # Set this in Render environment variables
    "port": int(os.getenv("DB_PORT", "3306")),
    "charset": "utf8",
    "use_unicode": True,
    "get_warnings": True,
    "raise_on_warnings": False,
    "connection_timeout": 30
}


def get_db_connection():
    """
    Create and return a database connection.
    Connection should be closed after use.
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        raise Exception(f"Database connection failed: {e}")


def test_connection():
    """Test the database connection"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return {"status": "success", "message": "Database connection successful"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
