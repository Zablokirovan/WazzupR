import os
import time
import requests
import db_data

from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

load_dotenv()


def chunks(num_list, size):
    for i in range(0, len(num_list), size):
        yield num_list[i:i + size]


def _create_session():
    session = requests.Session()

    retry = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST"]
    )

    adapter = HTTPAdapter(
        max_retries=retry,
        pool_connections=50,
        pool_maxsize=50
    )

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


def _send_one_message(session, url, headers, number, campaign_id, template, photo):
    data = {
        "channelId": "aeeb7d9e-0631-4ef4-a294-82dee4178089",
        "chatId": f"{number}",
        "chatType": "whatsapp",
        "templateId": f"{template}",
        "templateValues": [f"{photo}"]
    }

    try:
        response = session.post(url, headers=headers, json=data, timeout=20)

        try:
            response_json = response.json()
        except ValueError:
            response_json = {
                "error": "INVALID_JSON_RESPONSE",
                "response_text": response.text
            }

        db_data.insert_data_for_messages(campaign_id, response_json, response.status_code, number)

        return {
            "number": number,
            "status_code": response.status_code,
            "ok": response.ok,
            "text": response.text
        }

    except requests.RequestException as e:
        error_data = {
            "error": "REQUEST_EXCEPTION",
            "description": str(e)
        }

        db_data.insert_data_for_messages(campaign_id, error_data, 0, number)

        return {
            "number": number,
            "status_code": 0,
            "ok": False,
            "text": str(e)
        }


def sending_messages(num_list, campaign_id, city):
    url = "https://api.wazzup24.com/v3/message/"

    headers = {
        "Authorization": f"Bearer {os.getenv('WAZZUP_TOKEN')}",
        "Content-Type": "application/json"
    }
    numbers = [row[0] for row in num_list if row and row[0]]

    session = _create_session()
    cities_template = {
        'АЛА': {
            'template': 'ed5e4683-70bd-4370-9021-91ba8e3f65e1',
            'photo': 'https://em-go.kz/50.jpg'
        },

        'ТКР': {
            'template': 'a368e8ee-5952-439e-9270-59c044645fb9',
            'photo': 'https://em-go.kz/50.jpg'
        },
        'УСК': {
            'template': '66376ae8-ea86-45cf-87e3-6b453a911d3e',
            'photo': 'https://em-go.kz/50.jpg'
        },
        'ТРЗ': {
            'template': '940b421c-92b2-4f12-9772-b55f2188c5cd',
            'photo': 'https://em-go.kz/50.jpg'
        },
        'ШМК': {
            'template': '6ee39c87-3cee-4d9c-8f3f-98777b85d085',
            'photo': 'https://em-go.kz/50.jpg'
        }
    }
    city_template = cities_template.get(city)
    template = city_template['template']
    photo = city_template['photo']

    max_workers = 10
    batch_size = 300
    try:
        for batch in chunks(numbers, size=batch_size):
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(_send_one_message, session, url, headers, number, campaign_id, template, photo)
                    for number in batch
                ]

                for future in as_completed(futures):
                    result = future.result()
                    print(f"{result['number']} -> {result['status_code']}")

            time.sleep(2)

    finally:
        session.close()

    time.sleep(6)


def sending_messages_for_employee(num_list, campaign_id):
    url = "https://api.wazzup24.com/v3/message/"

    headers = {
        "Authorization": f"Bearer {os.getenv('WAZZUP_TOKEN')}",
        "Content-Type": "application/json"
    }

    session = _create_session()

    max_workers = 10
    batch_size = 300
    template = 'ed5e4683-70bd-4370-9021-91ba8e3f65e1'
    photo = 'https://em-go.kz/11.jpg'

    try:
        for batch in chunks(num_list, size=batch_size):
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(_send_one_message, session, url, headers, number, campaign_id, template, photo)
                    for number in batch
                ]

                for future in as_completed(futures):
                    result = future.result()
                    print(result["text"])

            time.sleep(2)

    finally:
        session.close()

    time.sleep(2)