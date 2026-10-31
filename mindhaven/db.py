import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="",
            database="mindhaven_db"
        )
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        return None
