import csv
import re

EXPECTED_COLS = 7


def normalize_fio(parts):
    """Разбивает первые 3 колонки на ФИО, приводит к Title Case, убирает лишние пробелы."""
    fio = " ".join(parts).split()
    return [part.title() if part else "" for part in (fio[:3] + ["", ""])]


def format_phone(phone):
    """Приводит телефон к +7(XXX)XXX-XX-XX доб.XXX"""
    if not phone or not phone.strip():
        return ""

    phone = phone.strip()

    # 1. Изолируем добавочный номер до очистки от символов
    ext_match = re.search(r'доб\.?\s*\(?\s*(\d+)\s*\)?', phone, re.IGNORECASE)
    ext = f" доб.{ext_match.group(1)}" if ext_match else ""

    # 2. Удаляем всё, что относится к добавочному, и оставляем только цифры основного номера
    base = re.sub(r'доб.*', '', phone, flags=re.IGNORECASE)
    digits = re.sub(r'\D', '', base)

    # 3. Нормализация длины и кода страны
    if len(digits) == 11 and digits[0] in ('7', '8'):
        digits = '7' + digits[1:]
    elif len(digits) == 10:
        digits = '7' + digits
    elif len(digits) != 11:
        return phone  # Нераспознанный формат возвращаем как есть

    # 4. Сборка в единый шаблон
    return f"+7({digits[1:4]}){digits[4:7]}-{digits[7:9]}-{digits[9:11]}{ext}"


# 1. Чтение и приведение к единой структуре
with open("phonebook_raw.csv", encoding="utf-8") as f:
    raw_rows = list(csv.reader(f, delimiter=","))

if not raw_rows:
    raise ValueError("Файл phonebook_raw.csv пуст.")

header = raw_rows[0][:EXPECTED_COLS]
# Дополняем заголовок, если колонок меньше ожидаемых
header += [""] * (EXPECTED_COLS - len(header))

contacts = []
for row in raw_rows[1:]:
    # Жёсткая обрезка или паддинг до EXPECTED_COLS
    if len(row) > EXPECTED_COLS:
        row = row[:EXPECTED_COLS]
    elif len(row) < EXPECTED_COLS:
        row += [""] * (EXPECTED_COLS - len(row))
    contacts.append(row)

# 2. Нормализация ФИО
for row in contacts:
    row[:3] = normalize_fio(row[:3])

# 3. Нормализация телефонов
for row in contacts:
    row[5] = format_phone(row[5])

# 4. Аккуратное объединение дублей
merged = {}
merged_count = 0

for row in contacts:
    # Ключ: фамилия + имя (регистронезависимо, без лишних пробелов)
    key = (row[0].strip().lower(), row[1].strip().lower())

    # Пропускаем строки, где нет ни фамилии, ни имени
    if not key[0] and not key[1]:
        continue

    if key in merged:
        for i in range(EXPECTED_COLS):
            target_val = merged[key][i].strip()
            source_val = row[i].strip()
            # Заполняем ТОЛЬКО пустые ячейки. Если обе заполнены, остаётся первая.
            if not target_val and source_val:
                merged[key][i] = source_val
        merged_count += 1
    else:
        # Сохраняем копию строки, чтобы избежать изменения оригинала
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