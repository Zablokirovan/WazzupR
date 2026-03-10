import requests

url = "https://api.wazzup24.com/v3/message/"

headers = {
    "Authorization": "Bearer b5e028025e6d4c7ba254089e48f59c8c",
    "Content-Type": "application/json"
}

data = {
    "channelId": "aeeb7d9e-0631-4ef4-a294-82dee4178089",
    "chatId": "77017888899",
    "chatType": "whatsapp",
    "text": "@template: fb36416e-5612-434d-8bab-5a91b1dd85ca { [[https://price.em-online.kz/2gis/full2.mp4]] }"
}

response = requests.post(url, headers=headers, json=data)

print(response.status_code)
print(response.text)