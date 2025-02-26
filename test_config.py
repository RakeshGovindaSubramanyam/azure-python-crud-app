from config import get_connection_string
import pyodbc

print("Testing connection...")
print(f"Connection string: {get_connection_string()}")
conn = pyodbc.connect(get_connection_string())
print("Connection successful!")
conn.close()
