import csv
import re

EXPECTED_COLS = 7

# Читаем адресную книгу
with open("phonebook_raw.csv", encoding="utf-8") as f:
    rows = csv.reader(f, delimiter=",")
    contacts_list = list(rows)

# защита от IndexError
for i in range(len(contacts_list)):
    if len(contacts_list[i]) < EXPECTED_COLS:
        contacts_list[i].extend([""] * (EXPECTED_COLS - len(contacts_list[i])))

# Нормализация ФИО
for row in contacts_list[1:]:
    fio_parts = " ".join(row[:3]).split()
    row[0] = fio_parts[0] if len(fio_parts) > 0 else ""
    row[1] = fio_parts[1] if len(fio_parts) > 1 else ""
    row[2] = fio_parts[2] if len(fio_parts) > 2 else ""


# Нормализация телефонов
def format_phone(phone):
    if not phone or not phone.strip():
        return ""
    phone = phone.strip()

    # Извлекаем добавочный номер
    ext_match = re.search(r'доб\.?\s*\(?(\d+)\)?', phone, re.IGNORECASE)
    ext = f" доб.{ext_match.group(1)}" if ext_match else ""

    # Оставляем только цифры основного номера
    digits = re.sub(r'\D', '', re.sub(r'доб.*', '', phone, flags=re.IGNORECASE))

    # Приводим к 11 цифрам с кодом 7
    if len(digits) == 11 and digits.startswith('8'):
        digits = '7' + digits[1:]
    elif len(digits) == 10:
        digits = '7' + digits
    elif len(digits) != 11:
        return phone + ext  # Нераспознанный формат возвращаем как есть

    return f"+7({digits[1:4]}){digits[4:7]}-{digits[7:9]}-{digits[9:11]}{ext}"


for row in contacts_list[1:]:
    row[5] = format_phone(row[5])

# АККУРАТНОЕ ОБЪЕДИНЕНИЕ ДУБЛЕЙ
contacts_dict = {}
for row in contacts_list[1:]:
    # По условию задачи: совпадение Фамилии и Имени = один человек
    key = (row[0], row[1])

    if key in contacts_dict:
        # Проходим по всем полям, начиная с Отчества
        for i in range(2, EXPECTED_COLS):
            # Заполняем ТОЛЬКО пустые ячейки, не затирая существующие данные
            if not contacts_dict[key][i].strip() and row[i].strip():
                contacts_dict[key][i] = row[i]
    else:
        contacts_dict[key] = row[:]  # Сохраняем копию строки

# Собираем итоговый список
contacts_list = [contacts_list[0]] + list(contacts_dict.values())

with open("phonebook.csv", "w", encoding="utf-8", newline='') as f:
    datawriter = csv.writer(f, delimiter=',')
    datawriter.writerows(contacts_list)

print(f"Обработка завершена. Уникальных записей: {len(contacts_list) - 1}")