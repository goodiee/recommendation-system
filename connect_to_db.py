import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def connect_and_load():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )
        print("Connected to the database!")
        return conn
    except Exception as e:
        print("Unable to connect to the database.")
        print(e)
        return None
