import pandas as pd
import re

# tactics.csv 読み込み
df = pd.read_csv("csv_data/tactics.csv", encoding="utf-8-sig")

# ⚠️ ランク列に 品質:◯種類:〜発動率:〜＋効果 が詰まっている

# ランクと効果に分割する処理
def split_rank_effect(text):
    if pd.isna(text):
        return "品質：不明", ""
    match = re.match(r"(品質：[SABC])種類：(.*)", text)
    if match:
        return match.group(1), match.group(2)
    else:
        return "品質：不明", text  # 種類：が無ければ全部を効果扱い

# 分割処理の適用
df[["ランク", "効果"]] = df["ランク"].apply(lambda x: pd.Series(split_rank_effect(x)))

# CSVを出力（元を上書きしたくない場合は tactics_clean.csv など）
df.to_csv("csv_data/tactics_clean.csv", index=False, encoding="utf-8-sig")
print("✅ tactics_clean.csv に整備完了")