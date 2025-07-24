import streamlit as st
import datetime
import pandas as pd
import os

# --- 関数 ---
@st.cache_data # ファイルの読み込み結果をキャッシュして高速化
def load_menu_data(year: int, month: int) -> pd.DataFrame | None:
    """指定された年月の献立CSVファイルを読み込み、DataFrameを返す"""
    file_path = f"{year}{month:02d}.csv"
    if not os.path.exists(file_path):
        return None
    try:
        # CSVを読み込む。1列目(day)をインデックスとして使用する
        df = pd.read_csv(file_path, index_col=0)
        return df
    except Exception as e:
        st.error(f"ファイルの読み込み中にエラーが発生しました: {e}")
        return None

def format_menu_display(menu_string: str) -> str:
    """献立の文字列を箇条書きのMarkdown形式に変換する"""
    if pd.isna(menu_string) or menu_string.strip() == "":
        return "データなし"
    if menu_string.strip() == "おやすみ":
        return "おやすみ"
    
    items = menu_string.split('・')
    return "\n".join(f"- {item.strip()}" for item in items)

# --- UI ---
st.title("献立表アプリ")
st.write("カレンダーから日付を選んで、昨日・今日・明日の献立を見ましょう。")

# --- 日付選択 ---
input_date = st.date_input(
    "日付を選択してください",
    value=datetime.date.today(),
)

# --- 献立表示 ---
st.header(f"{input_date.year}年{input_date.month}月の献立", divider="rainbow")

yesterday_date = input_date - datetime.timedelta(days=1)
tomorrow_date = input_date + datetime.timedelta(days=1)

for label, date_obj in [("昨日", yesterday_date), ("今日", input_date), ("明日", tomorrow_date)]:
    st.subheader(f"{label}（{date_obj.month}月{date_obj.day}日）")

    # 各日付に対応する月の献立データを読み込む
    menu_df = load_menu_data(date_obj.year, date_obj.month)

    if menu_df is not None:
        try:
            # DataFrameから日付(インデックス)で献立を取得
            menu = menu_df.loc[date_obj.day, 'menu']
            st.markdown(format_menu_display(menu))
        except KeyError:
            # DataFrameにその日のデータがない場合
            st.info("献立データがありません")
    else:
        # CSVファイルが見つからない場合
        st.info(f"{date_obj.year}年{date_obj.month}月の献立データが見つかりません。")
