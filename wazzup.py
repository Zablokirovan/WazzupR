import os

import requests
import time
import db_data

def chunks(num_list, size):
    for i in range(0, len(num_list), size):
        yield num_list[i:i + size]


def sending_messages(num_list):
    url = "https://api.wazzup24.com/v3/message/"

    headers = {
        "Authorization": f"Bearer {os.getenv("WAZZUP_TOKEN")}",
        "Content-Type": "application/json"
    }

    # превращаем [('7707...',), ('7706...',)] -> ['7707...', '7706...']
    numbers = [row[0] for row in num_list]

    batch = ['77752123690']
    #for batch in chunks(numbers, size=100):
    for number in batch:
        data = {
            "channelId": "aeeb7d9e-0631-4ef4-a294-82dee4178089",
            "chatId": number,
            "chatType": "whatsapp",
            "templateId": "a3238e71-9b93-48a4-a9ae-de81a69c867c",
            "templateValues": []
        }

        try:
            response = requests.post(url, headers=headers, json=data,
                                     timeout=20)
            db_data.insert_data_for_messages(response.json(), response.status_code)
        except requests.RequestException as e:
            print(f"{number} -> ERROR: {e}")

        time.sleep(0.5)

    time.sleep(4)