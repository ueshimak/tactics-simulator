import csv
import sqlite3

CSV_PATH = r"C:\Users\bxl07\Documents\信長シミュレータ\csv_data\tactics_unified.csv"
DB_PATH = r"C:\Users\bxl07\Documents\信長シミュレータ\officers.db"

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
        owners TEXT,
        trigger_rate REAL,
        source_type TEXT,
        function_type TEXT
    )
""")

with open(CSV_PATH, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if len(row) < 10:
            continue
        id_, name, type_, grade, rank, effect, owners, trigger_rate, source_type, function_type = row[:10]
        cur.execute("""
            INSERT INTO tactics(id, name, type, grade, rank, effect, owners, trigger_rate, source_type, function_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            int(id_), name, type_, grade, rank, effect, owners,
            float(trigger_rate), source_type, function_type
        ))

conn.commit()
conn.close()
print("✅ tactics テーブルを統合構造で再構築しました！")