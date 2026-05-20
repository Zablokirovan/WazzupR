import db_data
import wazzup
import pandas as pd

cityes = ['ALA', 'TKR', 'USK', 'TRZ','SHMK']

def main(cityes):

    # Запрашиваем данные о рассылке
    campaign_name   = input("Название рассылки (например: Рассылка №3 июнь 2026): ").strip()
    source          = input("Источник номеров (bitrix / retail): ").strip()
    notes           = input("Примечания (Enter чтобы пропустить): ").strip() or None

    # Создаём кампанию в БД и получаем campaign_id
    campaign_id = db_data.create_campaign(campaign_name, source, notes)
    print(f"Кампания создана, campaign_id = {campaign_id}")

    df = pd.read_csv('employee_phone.csv')
    phones = df["number"].tolist()
    wazzup.sending_messages_for_employee(phones, campaign_id)

    # Получаем номера и запускаем рассылку
    for city in cityes:
        num_list = db_data.get_number_info(city)
        print(f"Номеров для рассылки: {len(num_list)}")
        wazzup.sending_messages(num_list, campaign_id, city)



if __name__ == "__main__":
    main(cityes)