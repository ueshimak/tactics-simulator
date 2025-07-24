import json
import os
import random
import sqlite3

TEAM_DIR = "team_data"

def format武将名(unit):
    name = unit.get("武将名", "不明")
    if unit.get("所属") == "自軍":
        return f"<span style='color:#3182bd'>{name}</span>"  # 青系
    else:
        return f"<span style='color:#e74c3c'>{name}</span>"  # 赤系
    
def infer_team兵種(team):
    if "兵種" in team and team["兵種"]:
        return
    first = team["武将"][0]
    適性 = {
        "騎馬": first.get("騎馬適性", "A"),
        "足軽": first.get("足軽適性", "A"),
        "弓": first.get("弓適性", "A"),
        "鉄砲": first.get("鉄砲適性", "A"),
        "兵器": first.get("兵器適性", "A")
    }
    grade_order = {"S": 5, "A": 4, "B": 3, "C": 2}
    team["兵種"] = max(適性.items(), key=lambda x: grade_order.get(x[1], 0))[0]

def load_team(name):
    path = os.path.join(TEAM_DIR, f"{name}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_tactic_detail(name):
    conn = sqlite3.connect("officers.db")
    cur = conn.cursor()
    cur.execute("SELECT class, owners, effect, trigger_rate FROM tactics WHERE name = ?", (name,))
    res = cur.fetchone()
    conn.close()
    if res:
        発動方式 = res[0]
        対象 = res[1] if res[1] and res[1] != "不明" else infer_target_from_effect(res[2])
        return {
            "発動方式": 発動方式,
            "対象": 対象,
            "戦法効果": res[2],
            "発動率": res[3] if res[3] is not None else 0.3
        }
    return {"発動方式":"不明", "対象":"不明", "戦法効果":"", "発動率":0.3}

def infer_target_from_effect(effect_text):
    """戦法効果の文章から対象を推論する"""
    mapping = [
        ("自身", "自分"),
        ("自分", "自分"),
        ("味方それぞれ", "自軍全員"),
        ("自軍全員", "自軍全員"),
        ("自軍の大将", "自軍大将"),
        ("敵1人", "敵軍1人"),
        ("ランダムな敵1人", "敵軍ランダム1人"),
        ("ランダムな敵2人", "敵軍ランダム2人"),
        ("敵全員", "敵軍全員"),
        ("ランダムな味方2人", "自軍ランダム2人")
    ]
    for key, target in mapping:
        if key in effect_text:
            return target
    return "自分"  # ✅ 対象キーワードが見つからない場合は「自分」に補完


def parse_tactic_effect(effect):
    import re

    result = {
        "武勇補正": 0,
        "知略補正": 0,
        "統率補正": 0,
        "速度補正": 0,
        "状態異常": [],
        "武勇倍率": 1.0,
    }

    text = str(effect)

    # 🔍 武勇倍率抽出（例：「武勇攻撃300%」など）
    match = re.search(r"武勇[^\d]*(\d+)\s*[％%]", text)
    if match:
        result["武勇倍率"] = int(match.group(1)) / 100.0

    # 🔍 能力補正抽出（％を含む記述は除外）
    for stat in ["武勇", "知略", "統率", "速度"]:
        pattern = rf"{stat}(?!.*[%％])[^\d\-]*([\-]?\d+)\s*(増加|上昇|アップ|上がる|増える|減少|低下|減る|下がる)?"
        match = re.search(pattern, text)
        if match:
            amount = int(match.group(1))
            keyword = match.group(2)
            if keyword in ["減少", "低下", "減る", "下がる"]:
                amount *= -1
            result[f"{stat}補正"] += amount
        elif f"{stat}+20" in text and "%" not in text and "％" not in text:
            result[f"{stat}補正"] += 20
        elif stat in text and "増加" in text and "%" not in text and "％" not in text:
            result[f"{stat}補正"] += 100  # 曖昧表現はデフォルト加算（但し％含まず）

    # 🔍 状態異常抽出（表記揺れ対応あり）
    for status in ["混乱", "威嚇", "中毒", "火傷", "恐慌", "幻惑", "下剋上", "下克上", "挑発", "窮地"]:
        if status in text:
            normalized = "下剋上" if status == "下克上" else status
            result["状態異常"].append(normalized)

    return result



def apply_effect_to_unit(unit, effect_dict, log=None):
    unit.setdefault("状態", {})  # 安全な初期化

    # 📈 能力補正処理
    for stat in ["武勇", "知略", "統率", "速度"]:
        key = f"{stat}補正"
        val = effect_dict.get(key, 0)
        if val:
            before = unit["状態"].get(key, 0)
            after = before + val
            unit["状態"][key] = after
            if log:
                log.append(f"📈 {format武将名(unit)} の{stat}補正が {before} → {after} に変化（戦法効果）")

    # 💢 武勇耐性低下処理（例：剛力豪撃）
    if effect_dict.get("武勇耐性低下"):
        unit["状態"].setdefault("持続効果", []).append({
            "種類": "武勇耐性低下",
            "倍率": effect_dict["武勇耐性低下"],
            "残り": 1
        })
        if log:
            log.append(f"💢 {format武将名(unit)} → 武勇ダメージ耐性が一時的に低下（-{int(effect_dict['武勇耐性低下'] * 100)}%）")

    # 🛡️ 被ダメージ軽減処理（例：用心の命）
    if effect_dict.get("被ダメージ軽減"):
        unit["状態"]["被ダメージ軽減"] = {
            "倍率": effect_dict["被ダメージ軽減"],
            "残り": 3
        }
        if log:
            log.append(f"🛡️ {format武将名(unit)} → 被ダメージ軽減（-{int(effect_dict['被ダメージ軽減'] * 100)}%、3ターン）")

    # ⚠️ 状態異常処理
    for status in effect_dict.get("状態異常", []):
        unit["状態"].setdefault("状態異常", []).append(status)

        print("戦法効果（状態異常）：", status)

        if status == "幻惑":
            unit["状態"]["自律封印"] = 1
            if log:
                log.append(f"🔮 {format武将名(unit)} → 幻惑状態 → 次ターンの自律戦法封印")

        elif status == "窮地":
            unit["状態"]["自律封印回数"] = 2
            if log:
                log.append(f"🌀 {format武将名(unit)} → 窮地状態 → 自律戦法が2回行動前まで封印されます")

        elif status == "下剋上":
            if unit.get("配置順") == 0:
                if log:
                    log.append(f"🛡️ {format武将名(unit)} は大将 → 下剋上は無効 → 自軍への攻撃不可")
            else:
                unit["状態"]["行動対象強制"] = "大将"
                if log:
                    log.append(f"🗡️ {format武将名(unit)} → 下剋上付与 → 行動対象が敵大将に強制変更")

        elif status == "威嚇":
            unit["状態"]["行動スキップ残り"] = 2
            if log:
                log.append(f"⚠️ {format武将名(unit)} → 威嚇状態 → 次の2ターン行動不能")

        elif status == "挑発":
            unit["状態"]["挑発対象"] = effect_dict.get("挑発者名", "不明")
            unit["状態"]["挑発残りターン"] = 3
            if log:
                log.append(f"👊 {format武将名(unit)} → 挑発状態 → 通常攻撃対象が {unit['状態']['挑発対象']} に固定（3行動）")

        # ✅ 状態異常の付与記録（補足）
        if log:
            log.append(f"⚠️ {format武将名(unit)} に状態異常「{status}」が適用されました")
            
def apply_troop_aptitude(unit, team兵種):
    適性 = unit.get("兵種適性", {}).get(team兵種, "A")
    倍率 = {"S": 1.15, "A": 1.0, "B": 0.9, "C": 0.8}.get(適性, 1.0)
    for stat in ["統率", "武勇", "知略", "速度"]:
        unit["状態"][f"{stat}補正"] = int(unit.get(stat, 50) * 倍率)
    return f"[{format武将名(unit)}]の{team兵種}兵適正は{適性}で、能力調整は元の{倍率*100:.2f}%"
def get_general(team):
    return team["武将"][0]

def preparation_phase(team, label, log, enemy_team):
    log.append(f"🧭 {label}の準備フェーズ")
    general = get_general(team)
    formation = team.get("陣形", "")
    if formation:
        log.append(f"[{general['武将名']}]部隊の現在の陣形は{formation}です")

    if formation == "方円陣":
        for unit in team["武将"]:
            unit["状態"]["防御補正"] = 0.05
    elif formation == "偃月陣":
        for unit in team["武将"]:
            unit["状態"]["武勇補正"] = unit["状態"].get("武勇補正", 0) + 10

    for unit in team["武将"]:
        msg = apply_troop_aptitude(unit, team["兵種"])
        log.append(f"🧬 {msg}")
        for stat in ["武勇", "統率", "知略", "速度"]:
            before = unit["状態"].get(f"{stat}補正", 0)
            after = before + 20
            unit["状態"][f"{stat}補正"] = after
            log.append(f"[{format武将名(unit)}]は「{stat}之極意」効果を獲得し、{stat}補正が {before} → {after} に増加")

        for tactic in [unit["固有戦法"]] + unit["自由戦法"]:
            if tactic and tactic.get("戦法名"):
                detail = get_tactic_detail(tactic["戦法名"])
                if detail["発動方式"] in ["指揮", "受動"]:
                    log.append(f"⚙️ {format武将名(unit)} の準備戦法 → {tactic['戦法名']} 発動")
                    unit["状態"]["発動記録"]['戦法名'] = unit["状態"]["発動記録"].get('戦法名', 0) + 1
                    targets = {
                        "自分": [unit],
                        "自身": [unit],
                        "自軍全員": team["武将"],
                        "自軍大将": [general],
                        "自軍ランダム2人": random.sample([u for u in team["武将"] if u != unit], min(2, len(team["武将"]) - 1)),
                        "敵軍1人": [enemy_team["武将"][0]],
                        "敵軍ランダム1人": [random.choice(enemy_team["武将"])],
                        "敵軍ランダム2人": random.sample(enemy_team["武将"], min(2, len(enemy_team["武将"]))),
                        "敵軍全員": enemy_team["武将"]
                    }.get(detail["対象"], [])

                    effect_info = parse_tactic_effect(detail["戦法効果"])
                    print("戦法効果:", effect_info)
                    print("📦 戦法対象:", detail["対象"])
                    print("📦 対象数:", len(targets))

                    # 🎯 特殊戦法処理
                    if tactic["戦法名"] == "立花家の誇り":
                        for target in team["武将"]:
                            log.append(f"🌀 {format武将名(target)}に対する立花家の誇り効果が有効になりました")
                            if random.random() < 0.3:
                                target["状態"]["連撃付与"] = True

                    elif tactic["戦法名"] == "用心の命":
                        for target in targets:
                            target["状態"]["被ダメージ軽減"] = {"倍率": 0.2, "残り": 3}
                            log.append(f"🛡️ {format武将名(target)} は『用心の命』により被ダメージ -20%（3ターン）")

                    elif tactic["戦法名"] == "古今独歩":
                        changed_stats = []
                        for stat in ["武勇", "統率", "知略", "速度"]:
                            key = f"{stat}補正"
                            before = unit["状態"].get(key, 0)
                            after = before + 60
                            unit["状態"][key] = after
                            changed_stats.append(f"{stat}補正が {before} → {after}")
                        log.append(f"🧙 {format武将名(unit)} は古今独歩を発動 → " + "、".join(changed_stats))

                    elif tactic["戦法名"] == "威嚇の陣":
                        for _ in range(2):
                            enemy = random.choice(enemy_team["武将"])
                            知略 = unit["状態"].get("知略補正", unit.get("知略", 50))
                            rate = min(0.3 + 知略 * 0.17 / 100.0, 0.9)
                            enemy["状態"]["与ダメージ減少"] = {"倍率": rate, "残り": 3}
                            log.append(f"😱 {format武将名(enemy)} は威嚇の陣により与ダメージ -{int(rate*100)}%（3ターン）")

                    elif tactic["戦法名"] == "戦陣突破":
                        log.append(f"🔥 {format武将名(unit)} は戦陣突破を発動 → 統率無視＆武勇ダメージ+20%")
                        unit["状態"]["統率無視"] = True
                        effect_info["武勇倍率"] = effect_info.get("武勇倍率", 1.0) * 1.2
                        apply_effect_to_unit(unit, effect_info, log)

                    else:
                        for target in targets:
                            apply_effect_to_unit(target, effect_info, log)
                            if tactic["戦法名"] == "第六天の魔王":
                                unit["状態"]["魔王連撃"] = True
                                print(f"⚠️ 魔王連撃フラグ付与: {unit['武将名']}")

    log.append("")

def get_action_target(actor, target_team):
    actor_state = actor.get("状態", {})  # 念のため安全に取得
    武将一覧 = target_team.get("武将", [])

    # ⚠️ 行動対象強制（例：下剋上） → 敵軍大将に強制固定
    if actor_state.get("行動対象強制") == "大将":
        for u in 武将一覧:
            if u.get("配置順") == 0 and u.get("兵数", 0) > 0:
                return u
        # fallback: 最初の生存者 or ダミー
        alive = [u for u in 武将一覧 if u.get("兵数", 0) > 0]
        if alive:
            return alive[0]
        return {"武将名": "不明", "兵数": 0, "状態": {}, "配置順": -1}

    # ⚠️ 挑発状態 → 挑発元の武将名で対象強制変更
    挑発先名 = actor_state.get("挑発対象")
    if 挑発先名:
        for u in 武将一覧:
            if u.get("武将名") == 挑発先名 and u.get("兵数", 0) > 0:
                return u

    # 🧭 通常の攻撃対象（配置順で対面武将を指定）
    index = actor.get("配置順", 0)
    if 0 <= index < len(武将一覧):
        candidate = 武将一覧[index]
        if candidate.get("兵数", 0) > 0:
            return candidate

    # 🔁 fallback: 生存している敵武将からランダム
    alive = [u for u in 武将一覧 if u.get("兵数", 0) > 0]
    if alive:
        return random.choice(alive)

    # 💥 最終fallback: 部隊が空 or 全滅 → ダミーを返す
    return {"武将名": "不明", "兵数": 0, "状態": {}, "配置順": -1}

def handle_damage_triggered_buffs(actor, tactic, log):
    name = tactic.get("戦法名", "")
    buff_map = {
        "八幡大菩薩": {
            "倍率": 1.1,
            "能力": ["統率", "武勇", "知略", "速度"]
        },
        "剣神の咆哮": {
            "倍率": 1.2,
            "能力": ["武勇"]
        },
        "智勇双全": {
            "倍率": 1.1,
            "能力": ["知略", "武勇"]
        }
    }
    if name not in buff_map:
        return
    buff = buff_map[name]
    for stat in buff["能力"]:
        base = actor.get(stat, 50)
        current = actor["状態"].get(f"{stat}補正", base)
        boosted = int(current * buff["倍率"])
        actor["状態"][f"{stat}補正"] = boosted
        log.append(f"📈 {format武将名(actor)} → {name} により {stat}補正が {buff['倍率']*100:.0f}% 増加（{current}→{boosted}）")

def run_single_attack(actor, target_team, own_team, log, debug=False):
    # 🚫 自律戦法封印チェック
    if check_autonomous_seal(actor, log):
        return

    # ⚡ 自律戦法の発動処理
    try_autonomous_tactics(actor, target_team, log, debug)

    # 🗡️ 通常攻撃の処理
    target, damage = apply_regular_attack(actor, target_team, log, debug)

    # 💥 攻撃後のバフ反映（通常攻撃後）
    if damage > 0:
        for tactic in [actor["固有戦法"]] + actor["自由戦法"]:
            handle_damage_triggered_buffs(actor, tactic, log)

    # ⚡ 追撃戦法の発動処理
    try_follow_up_tactics(actor, target, log, debug)

def check_autonomous_seal(actor, log):
    if actor["状態"].get("自律封印回数", 0) > 0:
        actor["状態"]["自律封印回数"] -= 1
        log.append(f"🔒 {format武将名(actor)} は窮地状態のため自律戦法が封印中（残り {actor['状態']['自律封印回数']} 行動）")
        return True
    return False

def try_autonomous_tactics(actor, target_team, log, debug=False):
    for tactic in [actor["固有戦法"]] + actor["自由戦法"]:
        detail = get_tactic_detail(tactic["戦法名"])
        if detail["発動方式"] != "自律":
            continue

        boost = actor["状態"].get("戦法発動率補正", {}).get(tactic["戦法名"], 0.0)
        発動率 = detail["発動率"] + boost
        if random.random() < 発動率:
            log.append(f"⚡ 自律戦法 → {tactic['戦法名']} 発動（発動率:{int(発動率*100)}%）")
            effect = parse_tactic_effect(detail["戦法効果"])
            effect["発動者名"] = actor["武将名"]

            if "発動率増加" in effect.get("特殊", "") or tactic["戦法名"] == "連戦の戦い":
                actor.setdefault("状態", {}).setdefault("戦法発動率補正", {}).setdefault(tactic["戦法名"], 0.0)
                actor["状態"]["戦法発動率補正"][tactic["戦法名"]] += 0.10
                log.append(f"📈 {format武将名(actor)} の {tactic['戦法名']} の発動率が +10%（累積中）")

            targets = random.sample(
                [u for u in target_team["武将"] if u.get("兵数", 0) > 0],
                k=min(effect.get("対象数", 1), len(target_team["武将"]))
            )

            for target in targets:
                apply_effect_to_unit(target, effect, log)
                if effect.get("武勇倍率") or effect.get("知略倍率"):
                    base = "武勇" if effect.get("武勇倍率") else "知略"
                    multiplier = effect.get("武勇倍率") or effect.get("知略倍率")
                    damage = calculate_damage(actor, target, base, multiplier, log, debug)
                    target["兵数"] = max(0, target["兵数"] - damage)
                    emoji = "🟦" if actor["所属"] == "自軍" else "🟥"
                    log.append(f"{emoji} {format武将名(actor)} の自律 → {format武将名(target)} に {damage} ダメージ（残兵数: {target['兵数']}）")

def calculate_damage(actor, target, base_type, multiplier, log, debug=False):
    攻撃力 = 300 + actor["状態"].get(f"{base_type}補正", actor.get(base_type, 50))
    統率 = target["状態"].get("統率補正", target.get("統率", 50))
    軽減率 = min(統率 / 1500.0, 0.9)

    # 🧨 統率無視戦法の処理（例：戦陣突破）
    if actor.get("状態", {}).get("統率無視"):
        軽減率 = 0.0
        log.append(f"💥 {format武将名(actor)} は統率無視 → {format武将名(target)} の軽減率を無効化")

    # 💢 武勇耐性低下などの持続効果
    for eff in target["状態"].get("持続効果", []):
        if eff.get("種類") == "武勇耐性低下":
            軽減率 *= (1 - eff.get("倍率", 0.0))

    防御 = target["状態"].get("防御補正", 0.0)
    状態補正 = 1.0
    乱数補正 = random.uniform(0.95, 1.05)

    被補正 = 1.0
    if "被ダメージ軽減" in target["状態"]:
        val = target["状態"]["被ダメージ軽減"]["倍率"]
        被補正 *= (1 - val)

    与補正 = 1.0
    if "与ダメージ減少" in actor["状態"]:
        val = actor["状態"]["与ダメージ減少"]["倍率"]
        与補正 *= (1 - val)

    damage = int(攻撃力 * multiplier * 状態補正 * 乱数補正 * (1 - 軽減率) * (1 - 防御) * 被補正 * 与補正)

    if debug:
        log.append(
            f"[DEBUG] {format武将名(actor)} → {format武将名(target)}｜攻:{攻撃力}, 倍率:{multiplier}, 軽減:{軽減率:.2f}, 防御:{防御:.2f}, "
            f"被補:{被補正:.2f}, 与補:{与補正:.2f}, 乱数:{乱数補正:.2f}, 最終:{damage}"
        )
    return damage

def apply_regular_attack(actor, target_team, log, debug=False):
    target = get_action_target(actor, target_team)
    damage = calculate_damage(actor, target, "武勇", 1.0, log, debug)
    target["兵数"] = max(0, target["兵数"] - damage)
    emoji = "🟦" if actor["所属"] == "自軍" else "🟥"
    log.append(f"{emoji} {format武将名(actor)} の攻撃 → {format武将名(target)} に {damage} ダメージ（残兵数: {target['兵数']}）")
    return target, damage

def try_follow_up_tactics(actor, target, log, debug=False):
    for tactic in [actor["固有戦法"]] + actor.get("自由戦法", []):
        戦法名 = tactic.get("戦法名")
        if not 戦法名:
            continue

        detail = get_tactic_detail(戦法名)
        if detail.get("発動方式") != "追撃":
            continue

        発動率 = detail.get("発動率", 0)
        if random.random() < 発動率:
            log.append(f"⚡ {format武将名(actor)} が追撃戦法「{戦法名}」を発動")

            # ✅ 発動記録更新
            actor["状態"]["発動記録"][戦法名] = actor["状態"]["発動記録"].get(戦法名, 0) + 1

            effect = parse_tactic_effect(detail["戦法効果"])
            effect["発動者名"] = actor["武将名"]
            apply_effect_to_unit(target, effect, log)

            if effect.get("武勇倍率") or effect.get("知略倍率"):
                base = "武勇" if effect.get("武勇倍率") else "知略"
                multiplier = effect.get("武勇倍率") or effect.get("知略倍率")
                damage = calculate_damage(actor, target, base, multiplier, log, debug)
                target["兵数"] = max(0, target["兵数"] - damage)
                emoji = "🟦" if actor.get("所属") == "自軍" else "🟥"
                log.append(f"{emoji} {format武将名(actor)} の追撃 → {format武将名(target)} に {damage} ダメージ（残兵数: {target['兵数']}）")

                if damage > 0:
                    handle_damage_triggered_buffs(actor, tactic, log)
                
def simulate_battle(my_team_name, enemy_team_name, debug=False):
    my_team, enemy_team = initialize_battle(my_team_name, enemy_team_name)
    log = []

    # 🔧 各武将に発動記録初期化
    for team in [my_team, enemy_team]:
        for unit in team["武将"]:
            unit["状態"]["発動記録"] = {}
            for tactic in [unit["固有戦法"]] + unit.get("自由戦法", []):
                name = tactic.get("戦法名")
                if name:
                    unit["状態"]["発動記録"][name] = 0

    preparation_phase(my_team, "🟦 自軍", log, enemy_team)
    preparation_phase(enemy_team, "🟥 敵軍", log, my_team)

    for turn in range(1, 9):
        log.append(f"🔁 ターン {turn}")

        update_unit_states(my_team, enemy_team, log)
        trigger_reserved_tactics(my_team, enemy_team, log)
        apply_autonomous_actions(my_team, enemy_team, log)
        result = execute_actions(my_team, enemy_team, log, debug)
        if result == "victory":
            finalize_battle(my_team, enemy_team, log)
            log += format_battle_summary(my_team, enemy_team)
            return log
        check_special_conditions(my_team, enemy_team, log)

        log.append("")

    finalize_battle(my_team, enemy_team, log)
    log += format_battle_summary(my_team, enemy_team)

    if debug:
        for line in log:
            print(line)

    return log

def format_battle_summary(my_team, enemy_team):
    summary_log = []

    # ✅ 大将生存判定（配置順が 0 かつ兵数 > 0）
    def is_general_alive(team):
        return any(u.get("配置順") == 0 and u.get("兵数", 0) > 0 for u in team["武将"])

    my_general_alive = is_general_alive(my_team)
    enemy_general_alive = is_general_alive(enemy_team)

    if my_general_alive and enemy_general_alive:
        result = "✅ 勝敗：引き分け（両軍大将が生存）"
    elif my_general_alive:
        result = "✅ 勝敗：自軍の勝利（敵軍大将撃破）"
    elif enemy_general_alive:
        result = "✅ 勝敗：敵軍の勝利（自軍大将撃破）"
    else:
        result = "✅ 勝敗：引き分け（両軍大将とも撃破）"

    # ✅ 残兵数表示
    summary_log.append(result)
    summary_log.append(f"🟦 自軍残兵数： " + ", ".join(str(u.get("兵数", 0)) for u in my_team["武将"]))
    summary_log.append(f"🟥 敵軍残兵数： " + ", ".join(str(u.get("兵数", 0)) for u in enemy_team["武将"]))
    summary_log.append("")

    return summary_log

def initialize_battle(my_team_name, enemy_team_name):
    my_team = load_team(my_team_name)
    enemy_team = load_team(enemy_team_name)
    infer_team兵種(my_team)
    infer_team兵種(enemy_team)

    my_team["状態"] = {"大将攻撃回数": 0}
    enemy_team["状態"] = {"大将攻撃回数": 0}

    for team, 所属 in [(my_team, "自軍"), (enemy_team, "敵軍")]:
        for i, unit in enumerate(team["武将"]):
            unit["兵数"] = 12000
            unit["状態"] = {}
            unit["所属"] = 所属
            unit["配置順"] = i
            unit["兵種適性"] = {
                "騎馬": unit.get("騎馬適性", "A"),
                "足軽": unit.get("足軽適性", "A"),
                "弓": unit.get("弓適性", "A"),
                "鉄砲": unit.get("鉄砲適性", "A"),
                "兵器": unit.get("兵器適性", "A")
            }
            unit["統率"] = unit.get("統率", 50) + 120
            unit["武勇"] = unit.get("武勇", 50) + 120
            unit["知略"] = unit.get("知略", 50) + 120
            unit["速度"] = unit.get("速度", 50) + 50
    return my_team, enemy_team

def update_unit_states(my_team, enemy_team, log):
    for unit in my_team["武将"] + enemy_team["武将"]:
        if unit["兵数"] <= 0:
            continue

        # ✅ 状態異常ターンの更新・解除
        for key in ["自律封印", "行動スキップ残り"]:
            if unit["状態"].get(key, 0) > 0:
                unit["状態"][key] -= 1
                if unit["状態"][key] <= 0:
                    unit["状態"].pop(key)

        # ✅ 支援効果のターン更新・解除
        for buff_key in ["被ダメージ軽減", "与ダメージ増加", "与ダメージ減少"]:
            if unit["状態"].get(buff_key):
                unit["状態"][buff_key]["残り"] -= 1
                if unit["状態"][buff_key]["残り"] <= 0:
                    unit["状態"].pop(buff_key)

        # ✅ 持続効果（兵数回復など）のターン管理と発動
        effects = unit["状態"].get("持続効果", [])
        for eff in effects[:]:  # 安全なコピーでループ
            eff["残り"] -= 1
            if eff["残り"] <= 0:
                if eff.get("種類") == "兵数回復" and random.random() < eff.get("発動率", 0.75):
                    amount = unit.get("知略", 50) if eff.get("知略反映") else 500
                    unit["兵数"] += int(amount * eff.get("倍率", 1.0))
                    log.append(f"💚 {format武将名(unit)} の兵数が回復（+{int(amount)}）")
                effects.remove(eff)

def trigger_reserved_tactics(my_team, enemy_team, log):
    for unit in my_team["武将"] + enemy_team["武将"]:
        if unit["兵数"] <= 0:
            continue

        if unit["状態"].get("次ターン全体攻撃予約"):
            info = unit["状態"]["次ターン全体攻撃予約"]
            if unit["状態"].get("行動スキップ残り", 0) > 0 or unit["状態"].get("自律封印", 0) > 0:
                log.append(f"⚠️ {format武将名(unit)} は状態異常により『軍神の秘策』がキャンセルされました")
                unit["状態"].pop("次ターン全体攻撃予約")
                continue

            enemy_pool = my_team["武将"] if unit["所属"] == "敵軍" else enemy_team["武将"]
            alive = [u for u in enemy_pool if u.get("兵数", 0) > 0]
            倍率 = info["倍率"]
            武勇 = unit["状態"].get("武勇補正", unit.get("武勇", 50))

            for target in alive:
                統率 = target["状態"].get("統率補正", target.get("統率", 50))
                軽減率 = min(統率 / 1500.0, 0.9)
                防御 = target["状態"].get("防御補正", 0.0)
                状態補正 = 1.0
                乱数補正 = random.uniform(0.95, 1.05)

                damage = int((300 + 武勇) * 倍率 * 状態補正 * 乱数補正 * (1 - 軽減率) * (1 - 防御))
                target["兵数"] = max(0, target["兵数"] - damage)
                emoji = "🟦" if unit["所属"] == "自軍" else "🟥"
                log.append(f"{emoji} {format武将名(unit)} → 軍神の秘策発動 → {format武将名(target)} に {damage} ダメージ（残兵数: {target['兵数']}）")
            unit["状態"].pop("次ターン全体攻撃予約")

def apply_autonomous_actions(my_team, enemy_team, log):
    for unit in my_team["武将"] + enemy_team["武将"]:
        if unit["兵数"] <= 0:
            continue

        if unit["状態"].get("危地誘引フラグ"):
            if random.random() < 0.8:
                team = my_team if unit["所属"] == "自軍" else enemy_team
                targets = random.sample(team["武将"], min(2, len(team["武将"])))
                知略補正 = unit["状態"].get("知略補正", unit.get("知略", 50))
                rate = 0.2 + 知略補正 / 2000.0
                if random.random() < 0.5:
                    for target in targets:
                        target["状態"]["被ダメージ軽減"] = {"倍率": rate, "残り": 1}
                        log.append(f"🛡️ {format武将名(unit)} の危地誘引 → {format武将名(target)} に被ダメージ -{int(rate*100)}%（1ターン）")
                        unit["状態"]["発動記録"]["危地誘引"] = unit["状態"]["発動記録"].get("危地誘引", 0) + 1

                else:
                    for target in targets:
                        target["状態"]["与ダメージ増加"] = {"倍率": rate, "残り": 1}
                        log.append(f"⚔️ {format武将名(unit)} の危地誘引 → {format武将名(target)} に与ダメージ +{int(rate*100)}%（1ターン）")
                        unit["状態"]["発動記録"]["危地誘引"] = unit["状態"]["発動記録"].get("危地誘引", 0) + 1


def execute_actions(my_team, enemy_team, log, debug):
    units = sorted(my_team["武将"] + enemy_team["武将"], key=lambda x: x.get("速度", 50), reverse=True)
    for actor in units:
        if actor["兵数"] <= 0:
            continue

        log.append(f"▶️ {format武将名(actor)} の行動開始（速度:{actor.get('速度', 50)}）")

        if actor["状態"].get("行動スキップ残り", 0) > 0:
            actor["状態"]["行動スキップ残り"] -= 1
            log.append(f"😵 {format武将名(actor)} は威嚇のため行動できない（残り {actor['状態']['行動スキップ残り']}ターン）")
            continue

        target_team = enemy_team if actor["所属"] == "自軍" else my_team
        own_team = my_team if actor["所属"] == "自軍" else enemy_team

        repeat = 1
        if actor["状態"].get("魔王連撃"):
            repeat = 2
            log.append(f"👿 {format武将名(actor)} は第六天の魔王効果により2回攻撃を実施")
        elif actor["状態"].get("連撃付与") and random.random() < 0.3:
            repeat = 2
            log.append(f"🔁 {format武将名(actor)} は連撃判定に成功 → 2回攻撃実施")

        for _ in range(repeat):
            run_single_attack(actor, target_team, own_team, log, debug)

            if actor == get_general(own_team):
                own_team["状態"]["大将攻撃回数"] += 1

            if get_general(target_team)["兵数"] <= 0:
                log.append(f"🏆 勝利！{format武将名(get_general(target_team))} 撃破")
                return "victory"
    return "continue"

def check_special_conditions(my_team, enemy_team, log):
    for unit in my_team["武将"]:
        for tactic in [unit["固有戦法"]] + unit["自由戦法"]:
            if tactic.get("戦法名") == "半領の恩":
                if my_team["状態"]["大将攻撃回数"] >= 6:
                    my_team["状態"]["大将攻撃回数"] = 0
                    targets = random.sample(enemy_team["武将"], min(2, len(enemy_team["武将"])))
                    detail = get_tactic_detail(tactic["戦法名"])
                    effect = parse_tactic_effect(detail["戦法効果"])
                    for target in targets:
                        倍率 = effect.get("武勇倍率", 1.0)
                        武勇 = unit["状態"].get("武勇補正", unit.get("武勇", 50))
                        統率 = target["状態"].get("統率補正", target.get("統率", 50))
                        軽減率 = min(統率 / 1500.0, 0.9)
                        防御 = target["状態"].get("防御補正", 0.0)
                        状態補正 = 1.0
                        乱数補正 = random.uniform(0.95, 1.05)
                        damage = int((300 + 武勇) * 倍率 * 状態補正 * 乱数補正 * (1 - 軽減率) * (1 - 防御))
                        target["兵数"] = max(0, target["兵数"] - damage)
                        emoji = "🟦" if unit["所属"] == "自軍" else "🟥"
                        log.append(f"{emoji} {format武将名(unit)} の半領の恩 → {format武将名(target)} に {damage} ダメージ（残兵数: {target['兵数']}）")

def finalize_battle(my_team, enemy_team, log):
    my_hp = get_general(my_team)["兵数"]
    enemy_hp = get_general(enemy_team)["兵数"]
    log.append("⏳ 8ターン終了 → 判定処理")

    for unit in my_team["武将"]:
        log.append(f"🟦 自軍 [{format武将名(unit)}] 残兵数: {unit['兵数']}")
    for unit in enemy_team["武将"]:
        log.append(f"🟥 敵軍 [{format武将名(unit)}] 残兵数: {unit['兵数']}")

    if my_hp > 0 and enemy_hp > 0:
        log.append("🤝 引き分け（両軍大将が生存）")
    elif my_hp > enemy_hp:
        log.append(f"🏆 判定勝利（自軍:{my_hp} vs 敵軍:{enemy_hp}）")
    elif my_hp < enemy_hp:
        log.append(f"💀 判定敗北（自軍:{my_hp} vs 敵軍:{enemy_hp}）")
    else:
        log.append("🤝 引き分け（兵数同量）")