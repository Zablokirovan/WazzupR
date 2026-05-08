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

data = '2025-12-01'
data_end = '2026-03-14'
shema = 'MessagingCore'

def get_number_info():
    query = f"""
  SELECT ci.phone_num_clear
FROM "MessagingCore".contact_info ci
INNER JOIN "MessagingCore".contact_in_deal cid 
    ON cid.contact_id = ci.contact_id 
LEFT JOIN "MessagingCore".result_response_messagess rrm 
    ON rrm.phone_num = ci.phone_num_clear 
WHERE cid.date_create >= '2025-11-01'
  AND cid.date_create < '2025-12-31'
  AND ci.phone_num_clear IS NOT NULL
  AND rrm.messages_id IS NULL
GROUP BY ci.phone_num_clear
HAVING COUNT(DISTINCT ci.contact_id) = 1
LIMIT 4500;
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

        if resp_code == 201:
            sender_info = [(info_mess["chatId"], 'kaspi_WAZZUP', 'whatsapp')]
            cur.executemany("""
                INSERT INTO n8n.sender_map (
                    sender_id,
                    chanel_id,
                    chanel_type
                )
                VALUES (%s, %s, %s)
                ON CONFLICT (sender_id)
                DO UPDATE SET
                    chanel_id = EXCLUDED.chanel_id,
                    chanel_type = EXCLUDED.chanel_type
            """, sender_info)

    db_client.commit()
