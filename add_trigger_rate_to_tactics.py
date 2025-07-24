<<<<<<< HEAD
import csv
import re

INPUT_CSV = r"C:\Users\bxl07\Documents\信長シミュレータ\csv_data\tactics.csv"
OUTPUT_CSV = r"C:\Users\bxl07\Documents\信長シミュレータ\csv_data\tactics_with_rate.csv"

def parse_effect_and_trigger(text):
    m = re.match(r"(?:品質：)?[A-C]種類[:：]?(.*?)発動率[:：]?(\d+)%?(.*)", text)
    if m:
        trigger_way = m.group(1).strip()
        rate = int(m.group(2)) / 100
        effect = m.group(3).strip()
    else:
        rate = 0.3  # デフォルト
        effect = text.strip()
    return rate, effect

with open(INPUT_CSV, "r", encoding="utf-8") as f_in, open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f_out:
    reader = csv.reader(f_in)
    writer = csv.writer(f_out)
    headers = next(reader)
    headers.append("trigger_rate")
    writer.writerow(headers)

    for row in reader:
        if len(row) < 7:
            continue
        effect_text = row[5]
        rate, cleaned = parse_effect_and_trigger(effect_text)
        row[5] = cleaned
        row.append(str(rate))
        writer.writerow(row)

=======
import csv
import re

INPUT_CSV = r"C:\Users\bxl07\Documents\信長シミュレータ\csv_data\tactics.csv"
OUTPUT_CSV = r"C:\Users\bxl07\Documents\信長シミュレータ\csv_data\tactics_with_rate.csv"

def parse_effect_and_trigger(text):
    m = re.match(r"(?:品質：)?[A-C]種類[:：]?(.*?)発動率[:：]?(\d+)%?(.*)", text)
    if m:
        trigger_way = m.group(1).strip()
        rate = int(m.group(2)) / 100
        effect = m.group(3).strip()
    else:
        rate = 0.3  # デフォルト
        effect = text.strip()
    return rate, effect

with open(INPUT_CSV, "r", encoding="utf-8") as f_in, open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f_out:
    reader = csv.reader(f_in)
    writer = csv.writer(f_out)
    headers = next(reader)
    headers.append("trigger_rate")
    writer.writerow(headers)

    for row in reader:
        if len(row) < 7:
            continue
        effect_text = row[5]
        rate, cleaned = parse_effect_and_trigger(effect_text)
        row[5] = cleaned
        row.append(str(rate))
        writer.writerow(row)

>>>>>>> 6cc6e22068fd297841f9570f83ea405279f90609
print("✅ trigger_rate 列付き tactics_with_rate.csv を作成しました！")