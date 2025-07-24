<<<<<<< HEAD
import pandas as pd
import re

# tactics.csv を読み込む
df = pd.read_csv("csv_data/tactics.csv", encoding="utf-8-sig")

# 🔧 対象は種別が「伝授」の戦法だけ
def extract_quality_and_clean_name(row):
    if row["種別"] != "伝授":
        return row["ランク"], row["name"]  # 固有戦法はそのまま

    match = re.match(r"([SABC])(.+)", str(row["name"]))
    if match:
        rank = f"品質：{match.group(1)}"
        name = match.group(2).strip()
    else:
        rank = "品質：不明"
        name = row["name"]

    return rank, name

# ランクと名前の整備適用
df[["ランク", "name"]] = df.apply(extract_quality_and_clean_name, axis=1, result_type="expand")

# 🔄 tactics_clean.csv に保存（上書きしたければ tactics.csv）
df.to_csv("csv_data/tactics_clean.csv", index=False, encoding="utf-8-sig")
=======
import pandas as pd
import re

# tactics.csv を読み込む
df = pd.read_csv("csv_data/tactics.csv", encoding="utf-8-sig")

# 🔧 対象は種別が「伝授」の戦法だけ
def extract_quality_and_clean_name(row):
    if row["種別"] != "伝授":
        return row["ランク"], row["name"]  # 固有戦法はそのまま

    match = re.match(r"([SABC])(.+)", str(row["name"]))
    if match:
        rank = f"品質：{match.group(1)}"
        name = match.group(2).strip()
    else:
        rank = "品質：不明"
        name = row["name"]

    return rank, name

# ランクと名前の整備適用
df[["ランク", "name"]] = df.apply(extract_quality_and_clean_name, axis=1, result_type="expand")

# 🔄 tactics_clean.csv に保存（上書きしたければ tactics.csv）
df.to_csv("csv_data/tactics_clean.csv", index=False, encoding="utf-8-sig")
>>>>>>> 6cc6e22068fd297841f9570f83ea405279f90609
print("✅ tactics_clean.csv に伝授戦法の品質整備完了")