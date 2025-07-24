import streamlit as st
from logic_main import (
    handle_team_definition,
    handle_simulation_run,
    handle_optimizer_run,
    handle_db_build
)

def main():
    st.title("信長の野望 天下への道 編成ツール")

    # 🔹 メニュー選択
    menu = st.sidebar.selectbox("📚 メニューを選択", [
        "編成定義", 
        "戦闘シミュレーション", 
        "最適編成探索", 
        "データベース構築"
    ])

    is_public = False  # 公開モード制御（必要なら切り替え）

    if menu == "編成定義":
        handle_team_definition()
    elif menu == "戦闘シミュレーション":
        handle_simulation_run()
    elif menu == "最適編成探索":
        handle_optimizer_run()
    elif menu == "データベース構築":
        handle_db_build(is_public)

if __name__ == "__main__":
    main()