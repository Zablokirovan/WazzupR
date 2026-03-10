import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

db_client = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    port=os.getenv("DB_PORT")
)

def get_number_info():
    pass