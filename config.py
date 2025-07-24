# 公開モード切替（True → 公開版 / False → 開発版）
IS_PUBLIC_MODE = False

# CSVファイルのパス
CSV_PATH_GENERALS = "csv_data/generals.csv"
CSV_PATH_TACTICS = "csv_data/tactics.csv"
CSV_PATH_FORMATIONS = "csv_data/formations.csv"

# SQLiteデータベースのパス
DB_PATH = "database/nobunaga.db"

# 編成データの保存先（自軍・敵軍など）
TEAM_PATH_PLAYER = "csv_data/team_player.csv"
TEAM_PATH_ENEMY = "csv_data/team_enemy.csv"

# シミュレーション結果の保存パス
RESULT_PATH = "results/sim_result.csv"

# 最適編成候補の保存先（勝率上位など）
OPTIMAL_PATH = "results/best_combination.csv"

# Streamlitアプリのタイトル（必要であれば）
APP_TITLE = "天下への道 編成シミュレータ"

# 最大武将数（上限定義などに使用）
MAX_TEAM_SIZE = 3