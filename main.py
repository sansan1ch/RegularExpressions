import csv
import re

EXPECTED_COLS = 7
COLUMNS = ["lastname", "firstname", "surname", "organization", "position", "phone", "email"]


def normalize_fio(parts):
    """
    Разбивает первые 3 колонки на ФИО, приводит к Title Case, убирает лишние пробелы.
    Гарантирует возврат ровно 3 элементов, чтобы не ломать структуру строки.
    """
    fio = " ".join(parts).split()
    # Дополняем пустыми строками до 3 элементов и берём срез [:3]
    return [part.title() for part in (fio + ["", "", ""])[:3]]


def format_phone(phone):
    """
    Приводит телефон к виду +7(XXX)XXX-XX-XX или +7(XXX)XXX-XX-XX доб.XXX
    """
    if not phone or not phone.strip():
        return ""

    phone = phone.strip()

    # 1. Изолируем добавочный номер до очистки от символов
    ext_match = re.search(r'доб\.?\s*\(?\s*(\d+)\s*\)?', phone, re.IGNORECASE)
    # Ставим ровно один пробел перед "доб.", если добавочный найден
    ext = f" доб.{ext_match.group(1)}" if ext_match else ""

    # 2. Удаляем всё, что относится к добавочному, и оставляем только цифры основного номера
    base = re.sub(r'доб.*', '', phone, flags=re.IGNORECASE)
    digits = re.sub(r'\D', '', base)

    # 3. Нормализация длины и кода страны
    if len(digits) == 11 and digits[0] in ('7', '8'):
        digits = '7' + digits[1:]
    elif len(digits) == 10:
        digits = '7' + digits

    # Если после очистки длина не 11, возвращаем исходное значение (не ломаем данные)
    if len(digits) != 11:
        return phone

    # 4. Сборка в единый шаблон
    return f"+7({digits[1:4]}){digits[4:7]}-{digits[7:9]}-{digits[9:11]}{ext}"


# 1. Чтение и безопасное приведение к единой структуре
with open("phonebook_raw.csv", encoding="utf-8") as f:
    raw_rows = list(csv.reader(f, delimiter=","))

if not raw_rows:
    raise ValueError("Файл phonebook_raw.csv пуст.")

header = raw_rows[0][:EXPECTED_COLS]
header += [""] * (EXPECTED_COLS - len(header))

contacts = []
for row in raw_rows[1:]:
    # Явно гарантируем, что в каждой строке ровно EXPECTED_COLS элементов.
    # Это полностью исключает IndexError при дальнейшем доступе по row[i]
    if len(row) < EXPECTED_COLS:
        row += [""] * (EXPECTED_COLS - len(row))
    elif len(row) > EXPECTED_COLS:
        row = row[:EXPECTED_COLS]
    contacts.append(row)

# 2. Нормализация ФИО (теперь безопасно возвращает ровно 3 значения)
for row in contacts:
    row[:3] = normalize_fio(row[:3])

# 3. Нормализация телефонов и email
for row in contacts:
    row[5] = format_phone(row[5])
    row[6] = row[6].strip().lower() if row[6].strip() else ""

# 4. Аккуратное объединение дублей
merged = {}
merged_count = 0

for row in contacts:
    # Ключ: только Фамилия + Имя (без отчества и организации)
    key = (row[0].strip().lower(), row[1].strip().lower())

    # Пропускаем строки, где нет ни фамилии, ни имени
    if not key[0] and not key[1]:
        continue

    if key in merged:
        # Объединяем данные: заполняем ТОЛЬКО пустые ячейки
        for i in range(EXPECTED_COLS):
            target_val = merged[key][i].strip()
            source_val = row[i].strip()
            if not target_val and source_val:
                merged[key][i] = source_val
        merged_count += 1
    else:
        merged[key] = row[:]

# 5. Экспорт
result_rows = [header] + list(merged.values())

with open("phonebook.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(result_rows)

print(f"Обработка завершена")
print(f"Всего строк в исходнике: {len(raw_rows) - 1}")
print(f"Объединено дублей: {merged_count}")
print(f"Уникальных записей в result: {len(result_rows) - 1}")