import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def connect_and_load():
    try:
        conn = psycopg2.connect(os.getenv("DB_URL"))
        print("Connected to the database!")
        return conn
    except Exception as e:
        print("Unable to connect to the database.")
        print(e)
        return None
