import sqlite3
import json
import os
import random
from simulator import simulate_battle
from team_builder import build_team

DB_PATH = "officers.db"
TEAM_DIR = "team_data"

def get_all_officer_names():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 武将名 FROM officers")
    names = [row[0] for row in cursor.fetchall()]
    conn.close()
    return names

def get_random_formation():
    formations = ["横陣", "鶴翼", "魚鱗", "方円", "雁行"]
    types = ["騎馬", "弓", "鉄砲", "兵器", "足軽"]
    return random.choice(types), random.choice(formations)

def get_random_tactics(owner):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 戦法名, 戦法効果 FROM tactics WHERE 武将名 != ?", (owner,))
    all = cursor.fetchall()
    sampled = random.sample(all, 2)
    conn.close()
    return [{"戦法名": t[0], "戦法効果": t[1]} for t in sampled]

def generate_random_team(team_name):
    all_names = get_all_officer_names()
    selected = random.sample(all_names, 3)
    tactics_map = {name: get_random_tactics(name) for name in selected}
    兵種, 陣形 = get_random_formation()
    build_team(team_name, selected, tactics_map,兵種,陣形)

def optimizer(enemy_name="enemy_team", trial_count=100):
    print(f"🎲 敵軍 '{enemy_name}' に対する編成探索開始（試行数: {trial_count}）")
    enemy_path = os.path.join(TEAM_DIR, f"{enemy_name}.json")
    if not os.path.exists(enemy_path):
        generate_random_team(enemy_name)
    enemy_team = json.load(open(enemy_path, encoding="utf-8"))

    best_score = -1
    best_team_name = None

    for i in range(1, trial_count+1):
        team_name = f"candidate_{i}"
        generate_random_team(team_name)
        result = simulate_battle(team_name, enemy_name, debug=False)

        # 勝敗判定
        for line in result[::-1]:
            if "勝利" in line:
                win = 1
                break
            elif "敗北" in line:
                win = 0
                break
            else:
                win = 0

        print(f"試行{i}: 勝率 = {win}, 編成 = {team_name}")
        if win > best_score:
            best_score = win
            best_team_name = team_name

    print(f"\n✅ 最適編成: '{best_team_name}' 勝率 {best_score}")
    return best_team_name