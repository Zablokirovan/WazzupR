import db_data
import wazzup

def main():
    # Запрашиваем данные о рассылке
    campaign_name   = input("Название рассылки (например: Рассылка №3 июнь 2026): ").strip()
    source          = input("Источник номеров (bitrix / retail): ").strip()
    notes           = input("Примечания (Enter чтобы пропустить): ").strip() or None

    # Создаём кампанию в БД и получаем campaign_id
    campaign_id = db_data.create_campaign(campaign_name, source, notes)
    print(f"Кампания создана, campaign_id = {campaign_id}")

    # Получаем номера и запускаем рассылку
    num_list = db_data.get_number_info()
    print(f"Номеров для рассылки: {len(num_list)}")
    wazzup.sending_messages(num_list, campaign_id)

if __name__ == "__main__":
    main()