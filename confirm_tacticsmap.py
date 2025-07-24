<<<<<<< HEAD
import pandas as pd
import re

# 📥 tactics.csv の読み込み（指定パス）
csv_path = r"C:\Users\bxl07\Documents\信長シミュレータ\csv_data\tactics.csv"
df = pd.read_csv(csv_path, encoding="utf-8")

# 🎯 効果文から対象分類（target）を判定する関数
def detect_target(effect_text):
    text = str(effect_text)

    # 自軍大将だけが対象
    if re.search(r"(味方の大将に|自軍大将に|大将に対して)", text):
        return "自軍大将"

    # 自分自身
    if re.search(r"(自分|自身|発動者|自ら|自身の)", text):
        return "自分"

    # 自軍全員
    if re.search(r"(味方それぞれ|味方全体|自軍全体|味方にそれぞれ|味方に対して全員|味方全員|味方1人毎に)", text):
        return "自軍全員"

    # 自軍ランダム2人
    if re.search(r"(味方(2|二)人|味方2名|自軍(2|二)人|自軍2名)", text):
        return "自軍ランダム2人"

    # 敵軍全員
    if re.search(r"(敵全体|敵軍全体|敵すべて|敵全員|敵軍すべて)", text):
        return "敵軍全員"

    # 敵軍ランダム2人
    if re.search(r"(敵(2|二)人|敵2名|敵軍から2名|敵に2回攻撃|敵2体)", text):
        return "敵軍ランダム2人"

    # 敵軍ランダム1人
    if re.search(r"(敵(1|一)人|敵1名|敵軍から1名|敵1体|敵単体)", text):
        return "敵軍ランダム1人"

    # 敵軍1人（明示されずに単体処理）
    if re.search(r"(敵に.*攻撃|敵にダメージ|敵の.*能力|敵を妨害|敵に.*付与)", text):
        return "敵軍1人"

    # 内政系（戦闘対象なし）
    if re.search(r"(城下町|施設|銅銭|内政|資源|開発)", text):
        return "非戦闘"

    # 判定できない場合
    return "不明"

# 🧠 target 列生成（既存を優先）
target_list = []
for _, row in df.iterrows():
    effect_text = row.get("effect", "")
    existing_target = str(row.get("target", "")).strip()

    auto_target = detect_target(effect_text)
    final_target = existing_target if existing_target not in ["", "不明"] else auto_target
    target_list.append(final_target)

# 🔄 列を追加して保存
df["target"] = target_list
save_path = r"C:\Users\bxl07\Documents\信長シミュレータ\csv_data\tactics_with_target.csv"
df.to_csv(save_path, index=False, encoding="utf-8-sig")

=======
import pandas as pd
import re

# 📥 tactics.csv の読み込み（指定パス）
csv_path = r"C:\Users\bxl07\Documents\信長シミュレータ\csv_data\tactics.csv"
df = pd.read_csv(csv_path, encoding="utf-8")

# 🎯 効果文から対象分類（target）を判定する関数
def detect_target(effect_text):
    text = str(effect_text)

    # 自軍大将だけが対象
    if re.search(r"(味方の大将に|自軍大将に|大将に対して)", text):
        return "自軍大将"

    # 自分自身
    if re.search(r"(自分|自身|発動者|自ら|自身の)", text):
        return "自分"

    # 自軍全員
    if re.search(r"(味方それぞれ|味方全体|自軍全体|味方にそれぞれ|味方に対して全員|味方全員|味方1人毎に)", text):
        return "自軍全員"

    # 自軍ランダム2人
    if re.search(r"(味方(2|二)人|味方2名|自軍(2|二)人|自軍2名)", text):
        return "自軍ランダム2人"

    # 敵軍全員
    if re.search(r"(敵全体|敵軍全体|敵すべて|敵全員|敵軍すべて)", text):
        return "敵軍全員"

    # 敵軍ランダム2人
    if re.search(r"(敵(2|二)人|敵2名|敵軍から2名|敵に2回攻撃|敵2体)", text):
        return "敵軍ランダム2人"

    # 敵軍ランダム1人
    if re.search(r"(敵(1|一)人|敵1名|敵軍から1名|敵1体|敵単体)", text):
        return "敵軍ランダム1人"

    # 敵軍1人（明示されずに単体処理）
    if re.search(r"(敵に.*攻撃|敵にダメージ|敵の.*能力|敵を妨害|敵に.*付与)", text):
        return "敵軍1人"

    # 内政系（戦闘対象なし）
    if re.search(r"(城下町|施設|銅銭|内政|資源|開発)", text):
        return "非戦闘"

    # 判定できない場合
    return "不明"

# 🧠 target 列生成（既存を優先）
target_list = []
for _, row in df.iterrows():
    effect_text = row.get("effect", "")
    existing_target = str(row.get("target", "")).strip()

    auto_target = detect_target(effect_text)
    final_target = existing_target if existing_target not in ["", "不明"] else auto_target
    target_list.append(final_target)

# 🔄 列を追加して保存
df["target"] = target_list
save_path = r"C:\Users\bxl07\Documents\信長シミュレータ\csv_data\tactics_with_target.csv"
df.to_csv(save_path, index=False, encoding="utf-8-sig")

>>>>>>> 6cc6e22068fd297841f9570f83ea405279f90609
print("✅ tactics_with_target.csv に target 判定済みデータを保存しました")