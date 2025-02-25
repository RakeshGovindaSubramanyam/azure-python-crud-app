'''
#local

from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_SERVER = os.getenv("DATABASE_SERVER")
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_USERNAME = os.getenv("DATABASE_USERNAME")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")

def get_connection_string():
     return f"Driver={{ODBC Driver 17 for SQL Server}};Server={DATABASE_SERVER};Database={DATABASE_NAME};UID={DATABASE_USERNAME};PWD={DATABASE_PASSWORD}"

'''

import os

def get_connection_string():
    return (
        f"Driver={{ODBC Driver 17 for SQL Server}};"
        f"Server={os.getenv('DATABASE_SERVER')};"
        f"Database={os.getenv('DATABASE_NAME')};"
        f"UID={os.getenv('DATABASE_USERNAME')};"
        f"PWD={os.getenv('DATABASE_PASSWORD')};"
        f"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )
