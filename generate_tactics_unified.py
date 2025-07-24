import csv

INPUT_CSV = r"C:\Users\bxl07\Documents\信長シミュレータ\csv_data\tactics.csv"
OUTPUT_CSV = r"C:\Users\bxl07\Documents\信長シミュレータ\csv_data\tactics_unified.csv"

def guess_source_type(effect):
    if "味方" in effect:
        return "自軍"
    elif "敵" in effect:
        return "敵軍"
    else:
        return "不明"

def guess_function_type(effect):
    if "攻撃" in effect or "ダメージ" in effect:
        return "攻撃"
    elif "回復" in effect or "兵力" in effect:
        return "治療"
    elif "抵抗" in effect or "洞察" in effect or "援護" in effect:
        return "防御"
    elif "混乱" in effect or "恐慌" in effect or "丸腰" in effect or "威嚇" in effect:
        return "妨害"
    elif "浄化" in effect or "連撃" in effect or "反撃" in effect:
        return "補助"
    elif "産出量" in effect or "徴兵" in effect:
        return "内政"
    else:
        return "その他"

with open(INPUT_CSV, "r", encoding="utf-8") as f_in, open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f_out:
    reader = csv.reader(f_in)
    writer = csv.writer(f_out)
    headers = next(reader)
    headers += ["source_type", "function_type"]
    writer.writerow(headers)

    for row in reader:
        effect_text = row[5]
        source_type = guess_source_type(effect_text)
        function_type = guess_function_type(effect_text)
        row += [source_type, function_type]
        writer.writerow(row)

print("✅ tactics_unified.csv を自動生成しました！")