import pandas as pd
import sqlite3

# 📥 tactics_with_target.csv 読み込み
csv_path = r"C:\Users\bxl07\Documents\信長シミュレータ\csv_data\tactics_with_target.csv"
df = pd.read_csv(csv_path, encoding="utf-8")

# 🔌 SQLite データベースに接続
db_path = r"C:\Users\bxl07\Documents\信長シミュレータ\officers.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 🧭 各戦法に対して target を DB に更新
updated = 0
for _, row in df.iterrows():
    name = str(row["name"]).strip()
    target = str(row["target"]).strip()

    if name and target:
        cursor.execute("UPDATE tactics SET target = ? WHERE name = ?", (target, name))
        updated += 1

# 💾 コミットして終了
conn.commit()
conn.close()

print(f"✅ {updated} 件の戦法に target を反映しました → officers.db")