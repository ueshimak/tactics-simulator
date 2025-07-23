import pandas as pd
import re

# ✅ 固有戦法名と武将名のマップを作成
df_officers = pd.read_csv(r"C:\Users\bxl07\Documents\信長シミュレータ\csv_data/officers_fixed.csv", encoding="utf-8-sig")

# 🔧 戦法名整形関数（タブ・空白・（固有）表記の除去）
def normalize(text):
    if isinstance(text, str):
        text = re.sub(r"[\s\u3000\u0009]+", "", text)  # 空白・全角スペース・タブ除去
        text = text.replace("（固有）", "").replace("(固有)", "")
        return text.strip()
    return ""

# 🔧 辞書キーを整形してマップ作成
skill_to_owner = {
    normalize(row["固有戦法名"]): row["武将名"]
    for _, row in df_officers.iterrows()
    if pd.notna(row["固有戦法名"]) and pd.notna(row["武将名"])
}

# ✅ tactics.csv 読み込み
df_tactics = pd.read_csv(r"C:\Users\bxl07\Documents\信長シミュレータ\csv_data\tactics.csv", encoding="utf-8-sig")

# 🔧 name列を整形して補完用キー作成
df_tactics["name_clean"] = df_tactics["name"].apply(normalize)

# ✅ 所有者補完（種別='固有'で空欄のみ）
df_tactics["所有者"] = df_tactics.apply(
    lambda row: skill_to_owner.get(row["name_clean"]) if pd.isna(row["所有者"]) and row["種別"] == "固有" else row["所有者"],
    axis=1
)

# 🔧 整形列を削除して保存
df_tactics.drop(columns=["name_clean"], inplace=True)
df_tactics.to_csv(r"C:\Users\bxl07\Documents\信長シミュレータ\csv_data\tactics.csv", index=False, encoding="utf-8-sig")
print("✅ tactics.csv の所有者欄を武将名で補完しました（整形済）")