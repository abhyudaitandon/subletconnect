import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',       
            port=3306,                
            user='root',            
            password='@amantranS3#21',
            database='subletconnect'
        )
        if conn.is_connected():
            print("Connected to MySQL database.")
        return conn
    except Error as e:
        print(f"Error: {e}")
        return None