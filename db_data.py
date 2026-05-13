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
    query = """
        SELECT ci.phone_num_clear
        FROM "MessagingCore".contact_info ci
        INNER JOIN "MessagingCore".contact_in_deal cid
            ON cid.contact_id = ci.contact_id
        LEFT JOIN "MessagingCore".messaging_results mr
            ON mr.phone_num = ci.phone_num_clear
        WHERE cid.date_create >= '2025-11-01'
          AND cid.date_create < '2025-12-31'
          AND ci.phone_num_clear IS NOT NULL
          AND mr.messages_id IS NULL
        GROUP BY ci.phone_num_clear
        HAVING COUNT(DISTINCT ci.contact_id) = 1
        LIMIT 4500;
    """
    with db_client.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()


def create_campaign(name, source, notes=None):
    """Создаёт запись о рассылке и возвращает campaign_id"""
    with db_client.cursor() as cur:
        cur.execute("""
            INSERT INTO "MessagingCore".messaging_campaigns
                (name, source, notes)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (name, source, notes))
        campaign_id = cur.fetchone()[0]
    db_client.commit()
    return campaign_id


def insert_data_for_messages(campaign_id, info_mess, resp_code, number):
    """Пишет результат отправки сообщения в messaging_results"""
    if resp_code == 201:
        messages_id = info_mess.get("messageId")
        phone_num   = info_mess.get("chatId")
        error       = None
    else:
        messages_id = info_mess.get("requestId")
        phone_num   = number
        error       = info_mess.get("error")

    with db_client.cursor() as cur:
        cur.execute("""
            INSERT INTO "MessagingCore".messaging_results (
                campaign_id,
                messages_id,
                phone_num,
                response_code,
                status,
                error
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (messages_id)
            DO UPDATE SET
                response_code = EXCLUDED.response_code,
                status        = EXCLUDED.status,
                error         = EXCLUDED.error
        """, (campaign_id, messages_id, phone_num, resp_code, None, error))

        if resp_code == 201:
            cur.execute("""
                INSERT INTO n8n.sender_map (sender_id, chanel_id, chanel_type)
                VALUES (%s, %s, %s)
                ON CONFLICT (sender_id)
                DO UPDATE SET
                    chanel_id   = EXCLUDED.chanel_id,
                    chanel_type = EXCLUDED.chanel_type
            """, (info_mess.get("chatId"), 'kaspi_WAZZUP', 'whatsapp'))

    db_client.commit()