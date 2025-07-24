import csv
import sqlite3

CSV_PATH = r"C:\Users\bxl07\Documents\信長シミュレータ\csv_data\tactics.csv"
DB_PATH = r"C:\Users\bxl07\Documents\信長シミュレータ\officers.db"

# DB再構築
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS tactics")
cur.execute("""
    CREATE TABLE tactics (
        id INTEGER PRIMARY KEY,
        name TEXT,
        type TEXT,
        grade TEXT,
        rank TEXT,
        effect TEXT,
        owners TEXT
    )
""")

# CSV登録
with open(CSV_PATH, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader)  # ヘッダースキップ
    for row in reader:
        if len(row) < 7:
            continue
        id_, name, type_, grade, rank, effect, owners = row[:7]
        cur.execute("""
            INSERT INTO tactics(id, name, type, grade, rank, effect, owners)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (int(id_), name, type_, grade, rank, effect, owners))

conn.commit()
conn.close()

print("✅ tactics テーブルを tactics.csv に合わせて再構築しました！")