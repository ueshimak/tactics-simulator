import streamlit as st
from database import build_database
from team_builder import (
    build_team,
    list_teams,
    load_team,
    list_officer_names_by_rarity,
    get_officer_info,
    list_tactic_choices_by_rank_and_type
)
from simulator import simulate_battle
from optimizer import optimizer

NAME_MAP = {
    "立花闇千代": "立花誾千代",
}

def handle_db_build(is_public):
    if is_public:
        st.warning("🚫 公開モードではデータベース構築は無効です。")
    else:
        if st.button("データベースを構築する"):
            build_database()
            st.success("✅ SQLiteデータベースを構築しました。")

def handle_team_definition():
    st.subheader("👥 自軍編成の定義")
    team_name = st.text_input("編成名を入力", "my_team")

    existing_team = None
    if team_name in list_teams():
        existing_team = load_team(team_name)
        st.info(f"📝 既存編成 '{team_name}' を読み込みました。編集可能です。")
    else:
        existing_team = {
            "武将": [],
            "兵種": "足軽",
            "陣形": "方円陣"
        }
        st.info(f"🆕 新規編成 '{team_name}' を作成します")

    overrides = {}
    tactics_map = {}
    selected = []

    with st.expander("武将を選択（最大3人）"):
        rarity = st.selectbox("レアリティを選択", ["SSR", "SR", "R"])
        filtered_names = list_officer_names_by_rarity(rarity)
        default_selected = [w["武将名"] for w in existing_team["武将"]] if existing_team else []
        selected = st.multiselect("武将名（最大3人）", filtered_names, default=default_selected, max_selections=3)

    for name in selected:
        with st.expander(f"⚙️ {name} のステータス＆戦法設定"):
            lookup_name = NAME_MAP.get(name, name)
            officer = get_officer_info(lookup_name)

            # 📊 ステータス編集欄
            st.markdown(f"📊 {name} のステータス編集")
            edited_stats = {}
            for stat in ["統率", "武勇", "知略", "政治", "速度"]:
                default_val = next((o.get(stat, officer[stat]) for o in existing_team["武将"] if o["武将名"] == name), officer[stat])
                val = st.number_input(f"{stat}（{name}）", min_value=0, max_value=999, value=int(default_val), step=1, key=f"{name}_{stat}")
                edited_stats[stat] = int(val)
            overrides[name] = edited_stats

            # 固有戦法表示
            st.markdown(f"🛡️ 固有戦法：**{officer['固有戦法']['戦法名']}**")
            st.text_area(
                f"{name}の固有戦法効果",
                value=officer["固有戦法"]["戦法効果"],
                key=f"{name}_fixed",
                height=80,
                disabled=True
            )

            # 既存の自由戦法（読み込んだ編成がある場合）
            existing_tactics = []
            for o in existing_team["武将"]:
                if o["武将名"] == name:
                    existing_tactics = o.get("自由戦法", [])
                    break

            # 自由戦法①の設定
            st.markdown("🌀 自由戦法①の選択")
            rank1_default = existing_tactics[0].get("ランク") if len(existing_tactics) > 0 else "品質：S"
            trigger1_default = existing_tactics[0].get("発動方式") if len(existing_tactics) > 0 else "自律"
            rank1 = st.selectbox(f"{name}の戦法①ランク", ["品質：S", "品質：A", "品質：B"], index=["品質：S", "品質：A", "品質：B"].index(rank1_default), key=f"{name}_rank1")
            trigger1 = st.selectbox(f"{name}の戦法①発動方式", ["自律", "受動", "指揮", "追撃", "内政"], index=["自律", "受動", "指揮", "追撃", "内政"].index(trigger1_default), key=f"{name}_trigger1")
            choices1 = list_tactic_choices_by_rank_and_type(rank1, trigger1)
            options1 = [t["戦法名"] for t in choices1]
            default1 = existing_tactics[0]["戦法名"] if len(existing_tactics) >= 1 else options1[0]
            if default1 not in options1:
                options1 = [default1] + options1
            t1_name = st.selectbox(f"{name}の戦法①", options1, index=options1.index(default1), key=f"{name}_t1")
            t1_effect = next((t["戦法効果"] for t in choices1 if t["戦法名"] == t1_name), "")
            st.text_area(f"{name}の効果①", value=t1_effect, key=f"{name}_e1", height=60)

            # 自由戦法②の設定
            st.markdown("🌀 自由戦法②の選択")
            rank2_default = existing_tactics[1].get("ランク") if len(existing_tactics) > 1 else "品質：S"
            trigger2_default = existing_tactics[1].get("発動方式") if len(existing_tactics) > 1 else "自律"
            rank2 = st.selectbox(f"{name}の戦法②ランク", ["品質：S", "品質：A", "品質：B"], index=["品質：S", "品質：A", "品質：B"].index(rank2_default), key=f"{name}_rank2")
            trigger2 = st.selectbox(f"{name}の戦法②発動方式", ["自律", "受動", "指揮", "追撃", "内政"], index=["自律", "受動", "指揮", "追撃", "内政"].index(trigger2_default), key=f"{name}_trigger2")
            choices2 = list_tactic_choices_by_rank_and_type(rank2, trigger2)
            options2 = [t["戦法名"] for t in choices2]
            default2 = existing_tactics[1]["戦法名"] if len(existing_tactics) >= 2 else options2[0]
            if default2 not in options2:
                options2 = [default2] + options2
            t2_name = st.selectbox(f"{name}の戦法②", options2, index=options2.index(default2), key=f"{name}_t2")
            t2_effect = next((t["戦法効果"] for t in choices2 if t["戦法名"] == t2_name), "")
            st.text_area(f"{name}の効果②", value=t2_effect, key=f"{name}_e2", height=60)

            tactics_map[name] = [
                {"戦法名": t1_name, "戦法効果": t1_effect, "ランク": rank1, "発動方式": trigger1},
                {"戦法名": t2_name, "戦法効果": t2_effect, "ランク": rank2, "発動方式": trigger2}
            ]

    all兵種 = ["騎馬", "鉄砲", "弓", "兵器", "足軽"]
    all陣形 = ["包囲陣", "錐行陣", "方円陣", "衡軛陣", "偃月陣", "魚鱗陣", "雁行陣", "鶴翼陣", "鋒矢陣"]
    default_兵種 = existing_team.get("兵種", all兵種[0])
    default_陣形 = existing_team.get("陣形", all陣形[0])
    兵種 = st.selectbox("兵種を選択", all兵種, index=all兵種.index(default_兵種))
    陣形 = st.selectbox("陣形を選択", all陣形, index=all陣形.index(default_陣形))

    if st.button("編成を保存"):
        build_team(team_name, selected, tactics_map, overrides=overrides, 兵種=兵種, 陣形=陣形)
        st.success(f"✅ 編成 '{team_name}' を保存しました。")

def handle_simulation_run():
    st.subheader("⚔️ シミュレーション実行")
    my_team = st.selectbox("自軍編成を選択", list_teams())
    enemy_team = st.selectbox("敵軍編成を選択", list_teams())
    if st.button("戦闘開始"):
        log = simulate_battle(my_team, enemy_team, debug=False)
        st.success("✅ 戦闘シミュレーションが完了しました")
        for line in log:
            st.markdown(line, unsafe_allow_html=True)


def handle_optimizer_run():
    st.subheader("🧠 最強編成探索")
    enemy_team = st.text_input("敵編成名（存在しない場合は自動生成）", "enemy_team")
    trial_count = st.slider("試行回数（探索精度）", 10, 1000, 100)
    if st.button("探索開始"):
        best = optimizer(enemy_name=enemy_team, trial_count=trial_count)
        st.success(f"🏆 最適編成: {best}")