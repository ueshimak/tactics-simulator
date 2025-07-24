<<<<<<< HEAD
import sqlite3

conn = sqlite3.connect("officers.db")
cur = conn.cursor()

# まず、テーブル構造を確認（どんな列があるか）
cur.execute("PRAGMA table_info(tactics)")
columns = cur.fetchall()
print("📋 tacticsテーブルの列一覧:")
for col in columns:
    print(col)

# 次に、具体的なeffect列の中身を確認
cur.execute("SELECT name, effect FROM tactics WHERE effect IS NOT NULL")
results = cur.fetchall()

print("\n📎 effect列に説明文が入っている戦法一覧:")
for name, effect in results:
    print(f"🛡️ {name}: {effect}")

=======
import sqlite3

conn = sqlite3.connect("officers.db")
cur = conn.cursor()

# まず、テーブル構造を確認（どんな列があるか）
cur.execute("PRAGMA table_info(tactics)")
columns = cur.fetchall()
print("📋 tacticsテーブルの列一覧:")
for col in columns:
    print(col)

# 次に、具体的なeffect列の中身を確認
cur.execute("SELECT name, effect FROM tactics WHERE effect IS NOT NULL")
results = cur.fetchall()

print("\n📎 effect列に説明文が入っている戦法一覧:")
for name, effect in results:
    print(f"🛡️ {name}: {effect}")

>>>>>>> 6cc6e22068fd297841f9570f83ea405279f90609
conn.close()