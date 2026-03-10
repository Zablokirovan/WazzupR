import pandas as pd
import re
import math

df = pd.read_csv("CONTACT_20251208_18d3229a_693692b30fe4b.csv", dtype=str, sep=";")

phone_column = "Рабочий телефон"
TAG_VALUE = "Рассылка 11.12.2025"
ID = "ID"


def normalize_number(num: str):
    """Возвращает номер в формате +7XXXXXXXXXX или None."""
    if pd.isna(num):
        return None

    # Убираем всё, кроме цифр
    digits = re.sub(r"\D", "", num)

    # Ищем номер ровно из 11 цифр
    if len(digits) != 11:
        return None

    # Логика приведения
    if digits.startswith("8"):
        digits = "7" + digits[1:]
    elif digits.startswith("7"):
        pass
    else:
        # неизвестный случай — оставляем как есть
        pass

    return "+" + digits


def clean_one_number(raw):
    """Пытаемся взять первый валидный номер из строки с двумя номерами."""
    if pd.isna(raw):
        return None

    parts = [p.strip() for p in raw.split(",")]

    for p in parts:
        fmt = normalize_number(p)
        if fmt:
            return fmt

    return None


cleaned = []
id_value = []

if phone_column in df.columns:
    for val, cid in zip(df[phone_column], df[ID]):
        phone = clean_one_number(val)
        if phone:
            cleaned.append(phone)
            id_value.append(cid)
else:
    print(f"Колонка '{phone_column}' не найдена!")
    print(df.columns.tolist())
    exit()



# === Добавляем ТЕГ ===
result = pd.DataFrame({
    "Телефон": cleaned,
    "Тег": [TAG_VALUE] * len(cleaned),
    "ID": id_value
})

# === Сохраняем один общий файл ===
output_name = "contack_merged.csv"
result.to_csv(output_name, index=False, encoding="utf-8-sig")

print(f"Готово! Создан файл: {output_name}")
print("Всего номеров:", len(result))