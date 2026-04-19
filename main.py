import csv
import re

# Читаем адресную книгу в формате CSV
with open("phonebook_raw.csv", encoding="utf-8") as f:
    rows = csv.reader(f, delimiter=",")
    contacts_list = list(rows)

# Приводим ФИО к корректному виду (Фамилия, Имя, Отчество)
for row in contacts_list[1:]:
    fio = " ".join(row[:3]).split()
    # Если частей ФИО меньше трёх, дополняем пустыми строками
    row[0], row[1], row[2] = (fio + ["", "", ""])[:3]


def format_phone(phone):
    if not phone or not phone.strip():
        return ""
    phone = phone.strip()

    # Ищем добавочный номер (цифры после слова "доб", возможны скобки)
    ext_match = re.search(r'доб\.?\s*\(?(\d+)\)?', phone, re.IGNORECASE)
    ext = f" доб.{ext_match.group(1)}" if ext_match else ""

    # Отрезаем часть с добавочным номером и оставляем только цифры основного номера
    main_part = re.sub(r'доб.*', '', phone, flags=re.IGNORECASE)
    digits = re.sub(r'\D', '', main_part)

    # Приводим к 10 цифрам с кодом страны 7
    if len(digits) == 11 and digits.startswith('8'):
        digits = '7' + digits[1:]
    elif len(digits) == 10:
        digits = '7' + digits
    elif len(digits) != 11:
        return phone + ext  # Если формат не распознан, возвращаем как есть

    return f"+7({digits[1:4]}){digits[4:7]}-{digits[7:9]}-{digits[9:11]}{ext}"


for row in contacts_list[1:]:
    row[5] = format_phone(row[5])

contacts_dict = {}
for row in contacts_list[1:]:
    key = (row[0], row[1])
    if key in contacts_dict:
        # Проходим по полям: Отчество, Организация, Должность, Телефон, Email
        for i in range(2, 7):
            if not contacts_dict[key][i].strip() and row[i].strip():
                contacts_dict[key][i] = row[i]
    else:
        contacts_dict[key] = row[:]  # сохраняем копию строки


contacts_list = [contacts_list[0]] + list(contacts_dict.values())

with open("phonebook.csv", "w", encoding="utf-8", newline='') as f:
    datawriter = csv.writer(f, delimiter=',')
    datawriter.writerows(contacts_list)

print("Адресная книга успешно обработана и сохранена в phonebook.csv")