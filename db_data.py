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

def get_number_info(city):
    """Номера из Bitrix (contact_for_messaging). city - кириллический код (АЛА, ТКР, УСК, ТРЗ, ШМК)"""

    query = """
      SELECT DISTINCT ON (cfm.phone_num_clear)
        cfm.phone_num_clear,
        cfm.department_short
    FROM "MessagingCore".contact_for_messaging cfm
    WHERE cfm.date_create >= '2026-01-01' and cfm.department_short like %s
    ORDER BY
        cfm.phone_num_clear,
        cfm.date_create DESC;
    """
    with db_client.cursor() as cur:
        cur.execute(query, (f"{city}%",))
        return cur.fetchall()


def get_1c_number_info(city):
    """Номера из 1С (1cnumber), которых ещё нет в contact_info. city - кириллический код"""

    query = """
      SELECT
          CASE
              WHEN LEFT(c."НомерТелефона", 1) = '8'
              THEN '7' || SUBSTRING(c."НомерТелефона" FROM 2)
              ELSE c."НомерТелефона"
          END AS phone_with_7,
          c."Организация"
      FROM "MessagingCore"."1cnumber" c
      LEFT JOIN "MessagingCore".contact_info cfm
          ON RIGHT(cfm.phone_num_clear, 10) = RIGHT(c."НомерТелефона", 10)
      WHERE cfm.phone_num_clear IS NULL
        AND c."НомерТелефона" IS NOT NULL
        AND TRIM(c."НомерТелефона") <> ''
        AND c."Организация" like %s
      ORDER BY
          c."НомерТелефона" DESC;
    """
    with db_client.cursor() as cur:
        cur.execute(query, (f"{city}%",))
        return cur.fetchall()


def get_all_number_info(city):
    """Объединяет номера из Bitrix и 1С для города, убирая дубликаты по номеру"""

    bitrix_numbers = get_number_info(city)
    onec_numbers = get_1c_number_info(city)

    seen = set()
    merged = []
    for phone, label in bitrix_numbers + onec_numbers:
        key = phone[-10:] if phone else phone
        if key in seen:
            continue
        seen.add(key)
        merged.append((phone, label))

    return merged


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

    db_client.commit()