import sqlite3

FORMATION_DB_PATH = "formations.db"

def build_formation_db():
    conn = sqlite3.connect(FORMATION_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS formations")

    cursor.execute("""
    CREATE TABLE formations (
        name TEXT PRIMARY KEY,
        description TEXT,
        攻城補正 INTEGER,
        進軍速度補正 INTEGER,
        自律発動率補正 INTEGER,
        自律与ダメ補正 INTEGER,
        追撃与ダメ補正 INTEGER,
        被ダメ軽減 INTEGER,
        奇策率補正 INTEGER,
        会心率補正 INTEGER
    )
    """)

    formations = [
        ("包囲陣",     "敵を包み込み、攻略値+20。攻城戦に有利。",                     20, 0, 0, 0, 0, 0, 0, 0),
        ("錐行陣",     "先鋭で突き進む陣形。進軍速度+20。",                            0, 20, 0, 0, 0, 0, 0, 0),
        ("方円陣",     "周囲を守る防御型。自律戦法の被ダメージ -20%。",               0, 0, 0, 0, 0, 20, 0, 0),
        ("衡軛陣",     "車の横木のごとく統制の取れた陣。通常・追撃被ダメージ -20%。",  0, 0, 0, 0, 0, 20, 0, 0),
        ("偃月陣",     "半月状に構え、自律戦法の与ダメージ +20%。",                    0, 0, 0, 20, 0, 0, 0, 0),
        ("魚鱗陣",     "連撃の威力を強化。通常・追撃の与ダメージ +20%。",              0, 0, 0, 0, 20, 0, 0, 0),
        ("雁行陣",     "隊列の整った陣形。自律・追撃戦法の発動率 +5%。",              0, 0, 5, 0, 0, 0, 0, 0),
        ("鶴翼陣",     "広く展開して奇策を狙う。奇策率 +10%。",                        0, 0, 0, 0, 0, 0, 10, 0),
        ("鋒矢陣",     "矢じりの形で突撃。会心率 +10%。",                              0, 0, 0, 0, 0, 0, 0, 10),
    ]

    for f in formations:
        cursor.execute("""
        INSERT INTO formations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, f)

    conn.commit()
    conn.close()
    print("✅ formations.db（陣形効果データベース）を構築しました")

if __name__ == "__main__":
    build_formation_db()