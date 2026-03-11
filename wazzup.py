import requests
import time

def chunks(num_list, size):
    for i in range(0, len(num_list), size):
        yield num_list[i:i + size]


def sending_messages(num_list):
    url = "https://api.wazzup24.com/v3/message/"

    headers = {
        "Authorization": "Bearer b5e028025e6d4c7ba254089e48f59c8c",
        "Content-Type": "application/json"
    }

    # превращаем [('7707...',), ('7706...',)] -> ['7707...', '7706...']
    numbers = [row[0] for row in num_list]

    batch = ["77752123690", '77085658756', '77079367073']
    #for batch in chunks(numbers, size=100):
    for number in batch:
        data = {
            "channelId": "aeeb7d9e-0631-4ef4-a294-82dee4178089",
            "chatId": number,
            "chatType": "whatsapp",
            "text": "@template: fb36416e-5612-434d-8bab-5a91b1dd85ca { [[https://price.em-online.kz/2gis/full2.mp4]] }"
        }

        try:
            response = requests.post(url, headers=headers, json=data,
                                     timeout=20)
            print(f"{number} -> {response.status_code}")
            print(response.text)
        except requests.RequestException as e:
            print(f"{number} -> ERROR: {e}")

        time.sleep(3)