import mysql.connector
from mysql.connector import Error

def test_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='harryzayn1d',
            database='pesu_clubs_event_management'
        )
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"Connected to MySQL Server version {db_info}")
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            print(f"You're connected to database: {record[0]}")
            return True
        
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return False
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

# Only run this if the file is run directly (not imported)
if __name__ == "__main__":
    test_connection()