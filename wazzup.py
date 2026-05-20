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


def _send_one_message(session, url, headers, number, campaign_id, template_id, foto):
    data = {
        "channelId": "aeeb7d9e-0631-4ef4-a294-82dee4178089",
        "chatId": f"{number}",
        "chatType": "whatsapp",
        "templateId": f"{template_id}",
        "templateValues": [
            f"{foto}"
        ]
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


def sending_messages(num_list, campaign_id, city ):
    url = "https://api.wazzup24.com/v3/message/"

    headers = {
        "Authorization": f"Bearer {os.getenv('WAZZUP_TOKEN')}",
        "Content-Type": "application/json"
    }

    numbers = [(+77752123690)]#[row[0] for row in num_list if row and row[0]]

    session = _create_session()

    max_workers = 10
    batch_size = 300
    query_city = {
        'ALA':{
            "template_id":"435cc795-1f52-4d23-bd50-f613fe9e9a25",
            "foto":"https://em-go.kz/ala15.jpg"},
        "SHMK":{
            "template_id":"d418f0b7-7ec3-466f-8c95-9f17da387400",
            "foto":"https://em-go.kz/shmk15.jpg"},
        "TRZ":{
            "template_id":"f566a226-05bc-46e5-b5d6-2e6fa20991ee",
            "foto":"https://em-go.kz/trz15.jpg"},
        "TKR": {
            "template_id":"84a806ec-7971-43ee-a279-9ad6bf814b55",
            "foto":"https://em-go.kz/tkr15.jpg"},
        "USK":{
            "template_id":"bfc94ac6-be8c-492e-94d8-72cf405d599c",
            "foto":"https://em-go.kz/usk15.jpg"}
    }
    info = query_city.get(city)
    template_id = info["template_id"]
    foto = info["foto"]
    try:
        for batch in chunks(numbers, size=batch_size):
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(_send_one_message, session, url, headers, number, campaign_id, template_id, foto)
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

    template_id ="a50be0b4-1eed-446a-bd54-5c29dc745f96"
    foto = "https://em-go.kz/ala15.jpg"

    try:
        for batch in chunks(num_list, size=batch_size):
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(_send_one_message, session, url, headers, number, campaign_id, template_id, foto)
                    for number in batch
                ]

                for future in as_completed(futures):
                    result = future.result()
                    print(result["text"])

            time.sleep(2)

    finally:
        session.close()

    time.sleep(2)