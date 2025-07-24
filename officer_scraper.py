<<<<<<< HEAD
import time
import pandas as pd
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re

# ✅ 設定
EDGE_PATH = r"C:/Users/bxl07/AppData/Local/SeleniumBasic/edgedriver.exe"
URL_LIST_PAGE = "https://gamewith.jp/nobunagatenka/485928"
KAMIGAME_URL = "https://kamigame.jp/nobunagatenka/page/371287863528001044.html"
CSV_DIR = "csv_data"
DATA_CSV = os.path.join(CSV_DIR, "officers_fixed.csv")
NAME_CSV = os.path.join(CSV_DIR, "acquired_names.csv")

# ✅ 保存用CSVの初期化
os.makedirs(CSV_DIR, exist_ok=True)
if not os.path.exists(DATA_CSV):
    pd.DataFrame(columns=[
        "武将名", "統率", "武勇", "知略", "政治", "速度",
        "固有戦法名", "固有戦法効果", "レアリティ",
        "騎馬適性", "鉄砲適性", "弓適性", "兵器適性", "足軽適性"
    ]).to_csv(DATA_CSV, index=False, encoding="utf-8-sig")

if not os.path.exists(NAME_CSV):
    pd.DataFrame(columns=["武将名"]).to_csv(NAME_CSV, index=False, encoding="utf-8-sig")

# ✅ 神ゲー攻略から兵種特性マップ取得
def get兵種適性マップ():
    res = requests.get(KAMIGAME_URL)
    soup = BeautifulSoup(res.text, "lxml")
    rows = soup.select("#mainArticle > section > div:nth-child(1) > table > tbody > tr")

    特性マップ = {}
    for row in rows:
        cols = row.select("td")
        if len(cols) < 4:
            continue
        name_tag = cols[0].select_one("span a")
        if not name_tag:
            continue
        name = name_tag.text.strip()

        適性_soup = BeautifulSoup(str(cols[3]), "lxml")
        text = 適性_soup.get_text()

        matches = re.findall(r"【(.*?)】\s*([SABC])", text)
        特性 = {f"{兵種}適性": "A" for 兵種 in ["騎馬", "鉄砲", "弓", "兵器", "足軽"]}

        for 兵種名, ランク in matches:
            key = f"{兵種名.strip()}適性"
            if key in 特性:
                特性[key] = ランク

        特性マップ[name] = 特性

    return 特性マップ


兵種適性マップ = get兵種適性マップ()

# ✅ 取得済み武将名リスト
done_names = pd.read_csv(NAME_CSV)["武将名"].tolist()

# ✅ EdgeDriver起動
service = Service(executable_path=EDGE_PATH)
options = Options()
options.add_argument("user-agent=Mozilla/5.0")
options.add_argument("headless")
driver = webdriver.Edge(service=service, options=options)
wait = WebDriverWait(driver, 10)
driver.get(URL_LIST_PAGE)
time.sleep(5)

# ✅ 武将一覧テーブル行取得
rows = driver.find_elements(By.CSS_SELECTOR, "#article-body .nobutenka_listtable table tbody tr")

for idx in range(1, len(rows)):
    try:
        link_selector = f"#article-body .nobutenka_listtable table tbody tr:nth-child({idx+1}) td:nth-child(1) a"
        link_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, link_selector)))
        name = link_element.text.strip()

        rarity_selector = f"#article-body .nobutenka_listtable table tbody tr:nth-child({idx+1}) td:nth-child(2) img"
        try:
            rarity_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, rarity_selector)))
            rarity = rarity_element.get_attribute("alt").strip()
        except:
            rarity = ""

        if name in done_names:
            print(f"⏩ 既取得：{name}（スキップ）")
            continue

        print(f"\n🧭 武将{idx}: {name}（{rarity}） ページ遷移")
        driver.execute_script("arguments[0].scrollIntoView(true);", link_element)
        driver.execute_script("arguments[0].click();", link_element)
        time.sleep(5)
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#article-body table")
        ))

        soup = BeautifulSoup(driver.page_source, "lxml")

        def extract_stat(rank_idx: int) -> str:
            tag = soup.select_one(f".gw_bar_table tr:nth-child({rank_idx}) .rank b")
            return tag.text.strip() if tag else ""

        leadership = extract_stat(1)
        bravery    = extract_stat(2)
        intellect  = extract_stat(3)
        politics   = extract_stat(4)
        speed      = extract_stat(5)

        # ✅ 固有戦法名と効果抽出
        try:
            skill_name_tag = soup.select_one("#article-body > table:nth-child(21) > tbody > tr:nth-child(2) > td:nth-child(1)")
            skill_name = skill_name_tag.text.strip() if skill_name_tag else ""
        except:
            skill_name = ""

        try:
            effect_tag = soup.select_one("#article-body > table:nth-child(21) > tbody > tr:nth-child(2) > td:nth-child(2)")
            skill_effect = effect_tag.text.strip() if effect_tag else ""
        except:
            skill_effect = ""

        # ✅ 兵種特性マップから抽出（未登録なら Aで初期化）
        特性 = 兵種適性マップ.get(name, {f"{兵種}適性": "A" for 兵種 in ["騎馬", "鉄砲", "弓", "兵器", "足軽"]})

        row = {
            "武将名": name,
            "統率": leadership,
            "武勇": bravery,
            "知略": intellect,
            "政治": politics,
            "速度": speed,
            "固有戦法名": skill_name,
            "固有戦法効果": skill_effect,
            "レアリティ": rarity,
            **特性
        }

        pd.DataFrame([row]).to_csv(DATA_CSV, mode="a", header=False, index=False, encoding="utf-8-sig")
        pd.DataFrame([{"武将名": name}]).to_csv(NAME_CSV, mode="a", header=False, index=False, encoding="utf-8-sig")
        print(f"✅ 保存完了：{name}（{rarity}）")

        driver.back()
        time.sleep(4)

    except Exception as e:
        print(f"❌ エラー（武将{idx}）: {str(e)}")
        try:
            driver.get(URL_LIST_PAGE)
            time.sleep(5)
        except:
            print("⚠️ ページ再読み込み失敗、処理続行")
        continue

driver.quit()
=======
import time
import pandas as pd
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re

# ✅ 設定
EDGE_PATH = r"C:/Users/bxl07/AppData/Local/SeleniumBasic/edgedriver.exe"
URL_LIST_PAGE = "https://gamewith.jp/nobunagatenka/485928"
KAMIGAME_URL = "https://kamigame.jp/nobunagatenka/page/371287863528001044.html"
CSV_DIR = "csv_data"
DATA_CSV = os.path.join(CSV_DIR, "officers_fixed.csv")
NAME_CSV = os.path.join(CSV_DIR, "acquired_names.csv")

# ✅ 保存用CSVの初期化
os.makedirs(CSV_DIR, exist_ok=True)
if not os.path.exists(DATA_CSV):
    pd.DataFrame(columns=[
        "武将名", "統率", "武勇", "知略", "政治", "速度",
        "固有戦法名", "固有戦法効果", "レアリティ",
        "騎馬適性", "鉄砲適性", "弓適性", "兵器適性", "足軽適性"
    ]).to_csv(DATA_CSV, index=False, encoding="utf-8-sig")

if not os.path.exists(NAME_CSV):
    pd.DataFrame(columns=["武将名"]).to_csv(NAME_CSV, index=False, encoding="utf-8-sig")

# ✅ 神ゲー攻略から兵種特性マップ取得
def get兵種適性マップ():
    res = requests.get(KAMIGAME_URL)
    soup = BeautifulSoup(res.text, "lxml")
    rows = soup.select("#mainArticle > section > div:nth-child(1) > table > tbody > tr")

    特性マップ = {}
    for row in rows:
        cols = row.select("td")
        if len(cols) < 4:
            continue
        name_tag = cols[0].select_one("span a")
        if not name_tag:
            continue
        name = name_tag.text.strip()

        適性_soup = BeautifulSoup(str(cols[3]), "lxml")
        text = 適性_soup.get_text()

        matches = re.findall(r"【(.*?)】\s*([SABC])", text)
        特性 = {f"{兵種}適性": "A" for 兵種 in ["騎馬", "鉄砲", "弓", "兵器", "足軽"]}

        for 兵種名, ランク in matches:
            key = f"{兵種名.strip()}適性"
            if key in 特性:
                特性[key] = ランク

        特性マップ[name] = 特性

    return 特性マップ


兵種適性マップ = get兵種適性マップ()

# ✅ 取得済み武将名リスト
done_names = pd.read_csv(NAME_CSV)["武将名"].tolist()

# ✅ EdgeDriver起動
service = Service(executable_path=EDGE_PATH)
options = Options()
options.add_argument("user-agent=Mozilla/5.0")
options.add_argument("headless")
driver = webdriver.Edge(service=service, options=options)
wait = WebDriverWait(driver, 10)
driver.get(URL_LIST_PAGE)
time.sleep(5)

# ✅ 武将一覧テーブル行取得
rows = driver.find_elements(By.CSS_SELECTOR, "#article-body .nobutenka_listtable table tbody tr")

for idx in range(1, len(rows)):
    try:
        link_selector = f"#article-body .nobutenka_listtable table tbody tr:nth-child({idx+1}) td:nth-child(1) a"
        link_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, link_selector)))
        name = link_element.text.strip()

        rarity_selector = f"#article-body .nobutenka_listtable table tbody tr:nth-child({idx+1}) td:nth-child(2) img"
        try:
            rarity_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, rarity_selector)))
            rarity = rarity_element.get_attribute("alt").strip()
        except:
            rarity = ""

        if name in done_names:
            print(f"⏩ 既取得：{name}（スキップ）")
            continue

        print(f"\n🧭 武将{idx}: {name}（{rarity}） ページ遷移")
        driver.execute_script("arguments[0].scrollIntoView(true);", link_element)
        driver.execute_script("arguments[0].click();", link_element)
        time.sleep(5)
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#article-body table")
        ))

        soup = BeautifulSoup(driver.page_source, "lxml")

        def extract_stat(rank_idx: int) -> str:
            tag = soup.select_one(f".gw_bar_table tr:nth-child({rank_idx}) .rank b")
            return tag.text.strip() if tag else ""

        leadership = extract_stat(1)
        bravery    = extract_stat(2)
        intellect  = extract_stat(3)
        politics   = extract_stat(4)
        speed      = extract_stat(5)

        # ✅ 固有戦法名と効果抽出
        try:
            skill_name_tag = soup.select_one("#article-body > table:nth-child(21) > tbody > tr:nth-child(2) > td:nth-child(1)")
            skill_name = skill_name_tag.text.strip() if skill_name_tag else ""
        except:
            skill_name = ""

        try:
            effect_tag = soup.select_one("#article-body > table:nth-child(21) > tbody > tr:nth-child(2) > td:nth-child(2)")
            skill_effect = effect_tag.text.strip() if effect_tag else ""
        except:
            skill_effect = ""

        # ✅ 兵種特性マップから抽出（未登録なら Aで初期化）
        特性 = 兵種適性マップ.get(name, {f"{兵種}適性": "A" for 兵種 in ["騎馬", "鉄砲", "弓", "兵器", "足軽"]})

        row = {
            "武将名": name,
            "統率": leadership,
            "武勇": bravery,
            "知略": intellect,
            "政治": politics,
            "速度": speed,
            "固有戦法名": skill_name,
            "固有戦法効果": skill_effect,
            "レアリティ": rarity,
            **特性
        }

        pd.DataFrame([row]).to_csv(DATA_CSV, mode="a", header=False, index=False, encoding="utf-8-sig")
        pd.DataFrame([{"武将名": name}]).to_csv(NAME_CSV, mode="a", header=False, index=False, encoding="utf-8-sig")
        print(f"✅ 保存完了：{name}（{rarity}）")

        driver.back()
        time.sleep(4)

    except Exception as e:
        print(f"❌ エラー（武将{idx}）: {str(e)}")
        try:
            driver.get(URL_LIST_PAGE)
            time.sleep(5)
        except:
            print("⚠️ ページ再読み込み失敗、処理続行")
        continue

driver.quit()
>>>>>>> 6cc6e22068fd297841f9570f83ea405279f90609
print("\n📦 全処理完了。データ保存済み。")