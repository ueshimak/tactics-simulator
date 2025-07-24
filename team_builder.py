import sqlite3
import json
import os

DB_PATH = "officers.db"
BUILD_DIR = "team_data"
os.makedirs(BUILD_DIR, exist_ok=True)

# === 武将基本情報取得（兵種適性を含める） ===
def get_officer_info(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 武将名, 統率, 武勇, 知略, 政治, 速度,
               騎馬適性, 鉄砲適性, 弓適性, 兵器適性, 足軽適性
        FROM officers WHERE 武将名 = ?
    """, (name,))
    officer = cursor.fetchone()

    cursor.execute("""
        SELECT name, effect FROM tactics
        WHERE source_type = '固有' AND owners = ?
    """, (name,))
    tactics = cursor.fetchall()
    conn.close()

    if officer is None:
        return None

    info = {
        "武将名": officer[0],
        "統率": officer[1],
        "武勇": officer[2],
        "知略": officer[3],
        "政治": officer[4],
        "速度": officer[5],
        "騎馬適性": officer[6],
        "鉄砲適性": officer[7],
        "弓適性": officer[8],
        "兵器適性": officer[9],
        "足軽適性": officer[10],
        "固有戦法": {
            "戦法名": tactics[0][0] if tactics else "",
            "戦法効果": tactics[0][1] if tactics else ""
        },
        "自由戦法": []
    }
    return info

# === 自由戦法の割り当て ===
def assign_free_tactics(officer, tactic_list):
    officer["自由戦法"] = tactic_list[:2]
    return officer

# === チーム構築と保存（武将×兵種適性含む） ===
def build_team(team_name, members, tactics_map=None, overrides=None, 兵種="足軽", 陣形="包囲陣"):
    team = {
        "編成名": team_name,
        "兵種": 兵種,
        "陣形": 陣形,
        "武将": []
    }

    if len(members) > 3:
        print("⚠️ 最大3名までです")
        members = members[:3]

    for name in members:
        info = get_officer_info(name)
        if info:
            # ステータス補完処理
            stats = overrides.get(name) if overrides and name in overrides else {
                "統率": info.get("統率", 0),
                "武勇": info.get("武勇", 0),
                "知略": info.get("知略", 0),
                "政治": info.get("政治", 0),
                "速度": info.get("速度", 0)
            }
            for key in stats:
                info[key] = stats[key]

            # 自由戦法の割り当て（あれば）
            if tactics_map and name in tactics_map:
                info = assign_free_tactics(info, tactics_map[name])

            team["武将"].append(info)
        else:
            print(f"⚠️ 武将 '{name}' は存在しません")

    save_path = os.path.join(BUILD_DIR, f"{team_name}.json")
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(team, f, ensure_ascii=False, indent=2)
    print(f"✅ 編成 '{team_name}' を保存しました → {save_path}")

# === チーム読み込み（戦法も展開） ===
def load_team(team_name):
    path = os.path.join(BUILD_DIR, f"{team_name}.json")
    if not os.path.exists(path):
        print(f"❌ 編成 '{team_name}' は存在しません")
        return None

    with open(path, "r", encoding="utf-8") as f:
        team = json.load(f)
    return team

# === 保存済み編成一覧 ===
def list_teams():
    files = os.listdir(BUILD_DIR)
    teams = [f.replace(".json", "") for f in files if f.endswith(".json")]
    print("📂 保存編成一覧:", teams)
    return teams

# === 武将一覧取得 ===
def list_officer_names():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 武将名 FROM officers")
    names = [row[0] for row in cursor.fetchall()]
    conn.close()
    return names

# === レアリティで武将絞り込み ===
def list_officer_names_by_rarity(rarity):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 武将名 FROM officers WHERE レアリティ = ?", (rarity,))
    names = [row[0] for row in cursor.fetchall()]
    conn.close()
    return names

# === 戦法一覧（ランク指定） ===
def list_tactic_choices_by_rank(rank):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, effect FROM tactics
        WHERE rank = ? AND source_type = '伝授'
    """, (rank,))
    tactics = [{"戦法名": t[0], "戦法効果": t[1]} for t in cursor.fetchall()]
    conn.close()
    return tactics

# === 発動方式で戦法絞り込み ===
def list_tactic_choices_by_rank_and_trigger(rank, trigger_way):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print(f"[DEBUG] rank={rank}, trigger_way={trigger_way}（除外なし）")
    cursor.execute("""
        SELECT name, effect FROM tactics
        WHERE source_type = '伝授' AND rank = ? AND class = ?
    """, (rank, trigger_way))
    results = cursor.fetchall()
    print(f"[DEBUG] 候補件数: {len(results)}")
    tactics = [{"戦法名": t[0], "戦法効果": t[1]} for t in results]
    conn.close()
    return tactics

# === 発動方式・同義関数 ===
def list_tactic_choices_by_rank_and_type(rank, trigger_way):
    return list_tactic_choices_by_rank_and_trigger(rank, trigger_way)