<<<<<<< HEAD
import sqlite3

db_path = r"C:\Users\bxl07\Documents\信長シミュレータ\officers.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# target 列の追加
cursor.execute("ALTER TABLE tactics ADD COLUMN target TEXT")

conn.commit()
conn.close()
=======
import sqlite3

db_path = r"C:\Users\bxl07\Documents\信長シミュレータ\officers.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# target 列の追加
cursor.execute("ALTER TABLE tactics ADD COLUMN target TEXT")

conn.commit()
conn.close()
>>>>>>> 6cc6e22068fd297841f9570f83ea405279f90609
print("✅ tactics テーブルに target 列を追加しました")