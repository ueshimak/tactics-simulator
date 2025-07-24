import sqlite3
import pandas as pd
import os
import re

CSV_DIR = "csv_data"
OFFICERS_CSV = os.path.join(CSV_DIR, "officers_fixed.csv")
TACTICS_CSV = os.path.join(CSV_DIR, "tactics.csv")
DB_PATH = "officers.db"

def extract_trigger_type(class_text):
    class_text = str(class_text)
    for key in ["受動", "指揮", "自律", "追撃", "内政"]:
        if key in class_text:
            return key
    return "不明"

def extract_function_type(class_text):
    class_text = str(class_text)
    for key in ["攻撃", "補助", "治療", "防御"]:
        if key in class_text:
            return key
    return "不明"

def build_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 🧹 テーブル削除
    cursor.execute("DROP TABLE IF EXISTS officers;")
    cursor.execute("DROP TABLE IF EXISTS tactics;")

    # 🏗 officersテーブル再構築（兵種適性カラム追加！）
    cursor.execute("""
    CREATE TABLE officers (
        武将名 TEXT PRIMARY KEY,
        統率 INTEGER,
        武勇 INTEGER,
        知略 INTEGER,
        政治 INTEGER,
        速度 INTEGER,
        レアリティ TEXT,
        騎馬適性 TEXT,
        鉄砲適性 TEXT,
        弓適性 TEXT,
        兵器適性 TEXT,
        足軽適性 TEXT
    );
    """)

    # tacticsテーブル構築（変更なし）
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tactics (
        id INTEGER PRIMARY KEY,
        name TEXT,
        trigger_type TEXT,
        function_type TEXT,
        source_type TEXT,
        class TEXT,
        rank TEXT,
        effect TEXT,
        owners TEXT,
        trigger_rate REAL
    );
    """)

    # 📥 CSV読み込み
    df_officers = pd.read_csv(OFFICERS_CSV, encoding="utf-8-sig")
    df_tactics = pd.read_csv(TACTICS_CSV, encoding="utf-8-sig")

    # 🧠 tacticsカラム補完
    df_tactics["source_type"] = df_tactics["type"]
    df_tactics["trigger_type"] = df_tactics["class"].apply(extract_trigger_type)
    df_tactics["function_type"] = df_tactics["class"].apply(extract_function_type)
    df_tactics["rank"] = df_tactics["rank"].fillna("品質：不明")
    df_tactics["effect"] = df_tactics["effect"].fillna("")
    df_tactics["owners"] = df_tactics["owners"].fillna("")

    # 🚀 officers 登録（兵種適性含む！）
    for _, row in df_officers.iterrows():
        cursor.execute("""
        INSERT INTO officers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            row["武将名"],
            row["統率"],
            row["武勇"],
            row["知略"],
            row["政治"],
            row["速度"],
            row["レアリティ"],
            row.get("騎馬適性", "A"),
            row.get("鉄砲適性", "A"),
            row.get("弓適性", "A"),
            row.get("兵器適性", "A"),
            row.get("足軽適性", "A")
        ))

    # 🚀 tactics 登録（変更なし）
    for _, row in df_tactics.iterrows():
        cursor.execute("""
        INSERT INTO tactics (
            id, name, trigger_type, function_type,
            source_type, class, rank, effect, owners, trigger_rate
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            int(row["id"]),
            row["name"],
            row["trigger_type"],
            row["function_type"],
            row["source_type"],
            row["class"],
            row["rank"],
            row["effect"],
            row["owners"],
            row["trigger_rate"]
        ))

    conn.commit()
    conn.close()
    print("✅ officers.db を再構築しました（兵種適性反映済み）")

if __name__ == "__main__":
    build_database()