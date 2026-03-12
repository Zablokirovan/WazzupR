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


def insert_data_for_messages(info_mess, resp_code, number):
    """
    Function for adding information about transactions
     and contacts to the database
    """
    if resp_code ==201:
        info = [(info_mess["messageId"],info_mess["chatId"], resp_code, None, None)]
    else:
        info = [(info_mess["requestId"], number, resp_code, None, info_mess["error"])]

    with db_client.cursor() as cur:
        cur.executemany("""
                INSERT INTO "MessagingCore".result_response_messagess (
                    messages_id,
                    phone_num,
                    response_code,
                    status,
                    error
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (messages_id)
                DO UPDATE SET
                    phone_num = EXCLUDED.phone_num,
                    response_code = EXCLUDED.response_code,
                    status = EXCLUDED.status,
                    error = EXCLUDED.error
            """, info)

    db_client.commit()
