from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import os
import re

# 戦法名整形（全角・注釈・タブ除去）
def clean_tactic_name(text):
    return re.sub(r"[（(].*?[）)]", "", str(text)).replace("\t", "").replace("　", "").strip()

# 発動率抽出（発動率:○○% → 0.○○）
def extract_trigger_rate(text):
    match = re.search(r"発動率[:：]?\s*(\d+)%", str(text))
    if match:
        return float(match.group(1)) / 100
    return 0.3

# 種類（class）と効果（effect）を分離
def extract_class_and_effect(text):
    match = re.search(r"種類[:：](受動|指揮|自律|追撃|内政)(.*)", str(text).strip())
    if match:
        class_type = match.group(1)
        effect_body = match.group(2).strip()
        return class_type, effect_body
    return "不明", text.strip()

def fetch_fixed_tactics(url, officer_csv_path="csv_data/officers_fixed.csv"):
    os.makedirs("csv_data", exist_ok=True)

    # 所有者マッピング（武将名 ⇔ 戦法名）
    tactic_owner_map = {}
    if os.path.exists(officer_csv_path):
        df_officers = pd.read_csv(officer_csv_path, encoding="utf-8-sig")
        if "固有戦法名" in df_officers.columns and "武将名" in df_officers.columns:
            df_officers["clean_name"] = df_officers["固有戦法名"].apply(clean_tactic_name)
            tactic_owner_map = dict(zip(df_officers["clean_name"], df_officers["武将名"]))
        else:
            print("⚠️ officers_fixed.csv に必要な列が見つかりません")
    else:
        print("⚠️ officers_fixed.csv が見つかりません → 所有者補完スキップ")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#mainArticle > section > table:nth-child(7)"))
        )
        print("✅ 固有戦法テーブル表示確認")
    except:
        print("⚠️ 固有戦法テーブル読み込み失敗")
        driver.quit()
        return []

    soup = BeautifulSoup(driver.page_source, 'lxml')
    driver.quit()

    table = soup.select_one("#mainArticle > section > table:nth-child(7)")
    if not table:
        print("⚠️ 固有戦法テーブル見つかりません")
        return []

    rows = table.find_all('tr')
    tactics = []

    for row in rows:
        img_tag = row.find('img')
        if not img_tag or not img_tag.get('alt'):
            continue  # ⚠️ 見出し行などを安全にスキップ

        cols = row.find_all('td')
        if len(cols) < 2:
            continue


        img_tag = cols[0].select_one('span picture img')
        raw_name = img_tag['alt'].strip() if img_tag and 'alt' in img_tag.attrs else "名称取得失敗"
        name = clean_tactic_name(raw_name)

        details = cols[1].text.strip().split('\n')
        raw_effect = details[0].strip() if details else ""

        # 品質抽出
        match = re.match(r"品質[:：]([SABC])", raw_effect)
        rank = f"品質：{match.group(1)}" if match else "品質：不明"

        class_type, effect_body = extract_class_and_effect(raw_effect)
        trigger_rate = extract_trigger_rate(raw_effect)
        owners = tactic_owner_map.get(name, "")

        tactics.append({
            'id': len(tactics) + 1,
            'name': name,
            'type': "固有",
            'rank': rank,
            'class': class_type,
            'effect': effect_body,
            'owners': owners,
            'trigger_rate': trigger_rate
        })

    print(f"✅ 固有戦法取得：{len(tactics)}件（所有者付き：{sum(1 for t in tactics if t['owners'])}件）")
    return tactics

def fetch_transferable_tactics(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".nobu_skill_table table"))
        )
        print("✅ 伝授戦法テーブル表示確認")
    except:
        print("⚠️ 伝授戦法テーブル読み込み失敗")
        driver.quit()
        return []

    soup = BeautifulSoup(driver.page_source, 'lxml')
    driver.quit()

    rows = soup.select(".nobu_skill_table table tbody tr")[1:]
    tactics = []

    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 3:
            continue

        raw_name = cols[0].text.strip()
        skill_type = cols[1].text.strip()
        effect = cols[2].text.strip()

        match = re.match(r"([SABC])(.+)", raw_name)
        rank = f"品質：{match.group(1)}" if match else "品質：不明"
        name = match.group(2).strip() if match else raw_name

        class_type = skill_type[:2] if len(skill_type) >= 2 else "不明"
        match = re.search(r"(発動率|【確率】)\s*[:：]?\s*(\d+)%", effect)
        trigger_rate = float(match.group(2)) / 100 if match else 0.3


        tactics.append({
            'id': None,
            'name': name,
            'type': "伝授",
            'rank': rank,
            'class': class_type,
            'effect': effect,
            'owners': "",
            'trigger_rate': trigger_rate
        })


    print(f"✅ 伝授戦法取得：{len(tactics)}件")
    return tactics

# 実行ブロック
if __name__ == "__main__":
    os.makedirs("csv_data", exist_ok=True)
    fixed_url = "https://kamigame.jp/nobunagatenka/page/371416793312459138.html"
    transferable_url = "https://gamewith.jp/nobunagatenka/503928"

    fixed = fetch_fixed_tactics(fixed_url)
    transferable = fetch_transferable_tactics(transferable_url)

    combined = fixed + transferable
    for i, row in enumerate(combined):
        row['id'] = i + 1

    df = pd.DataFrame(combined)
    df.to_csv("csv_data/tactics.csv", index=False, encoding="utf-8-sig")
    print(f"📦 tactics.csv 保存完了（総数: {len(combined)}）")