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

data = '2026-01-01'
shema = 'MessagingCore'

def get_number_info():
    query = f"""
    select distinct civ.phone_num_clear 
    from "{shema}".contact_info_view civ 
    where civ.date_create <= '{data}'
     and civ.phone_num_clear like '77%';
    """
    with db_client.cursor() as cur:
        cur.execute(query)
        result = cur.fetchall()
        return result
