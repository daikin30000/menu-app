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
st.write("年月と日付を選んで、昨日・今日・明日の献立を見ましょう。")

# --- 年月選択 ---
today = datetime.date.today()
col1, col2 = st.columns(2)
with col1:
    # 年の選択。過去5年から未来1年までを選択肢にする
    year_options = range(today.year - 5, today.year + 2)
    selected_year = st.selectbox("年", options=year_options, index=list(year_options).index(today.year))
with col2:
    selected_month = st.selectbox("月", options=range(1, 13), index=today.month - 1)

# --- 献立データ読み込み ---
menu_df = load_menu_data(selected_year, selected_month)

if menu_df is None:
    st.error(f"{selected_year}年{selected_month}月の献立データが見つかりません。")
    st.info(f"ヒント: アプリと同じフォルダに `{selected_year}{selected_month:02d}.csv` という名前のファイルを作成してください。")
else:
    st.success(f"{selected_year}年{selected_month}月の献立を読み込みました。")
    
    # --- 日付選択 ---
    first_day_of_month = datetime.date(selected_year, selected_month, 1)
    # 月の最終日を安全に取得
    if selected_month == 12:
        last_day_of_month = datetime.date(selected_year, 12, 31)
    else:
        last_day_of_month = datetime.date(selected_year, selected_month + 1, 1) - datetime.timedelta(days=1)

    # 今日の日付が選択された月と同じなら今日を、違うならその月の1日をデフォルトに
    if today.year == selected_year and today.month == selected_month:
        default_date = today
    else:
        default_date = first_day_of_month

    input_date = st.date_input(
        "日付を選択してください",
        value=default_date,
        min_value=first_day_of_month,
        max_value=last_day_of_month,
    )

    # --- 献立表示 ---
    yesterday_date = input_date - datetime.timedelta(days=1)
    tomorrow_date = input_date + datetime.timedelta(days=1)

    for label, date_obj in [("昨日", yesterday_date), ("今日", input_date), ("明日", tomorrow_date)]:
        st.subheader(f"{label}（{date_obj.month}月{date_obj.day}日）")
        
        # 選択された月と同じ月のデータのみ表示
        if date_obj.month == selected_month:
            try:
                # DataFrameから日付(インデックス)で献立を取得
                menu = menu_df.loc[date_obj.day, 'menu']
                st.markdown(format_menu_display(menu))
            except KeyError:
                # DataFrameにその日のデータがない場合
                st.info("献立データがありません")
        else:
            # 月が違う場合はデータなし
            st.info("献立データがありません")
