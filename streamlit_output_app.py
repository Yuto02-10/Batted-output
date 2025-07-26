import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw
import os

# --- 定数と定義 ---
BASEBALL_FIELD_IMG = 'baseballfield.jpg'
DATA_FILENAME = 'hitting_data.csv'
IMAGE_SIZE = (750, 750)

# 色と形の定義
HIT_TYPE_COLORS = {
    'ゴロ': 'green', 'フライ': 'blue', 'ライナー': 'red',
    '三振': 'black', '四死球': 'purple', 'その他': 'gray'
}
PITCH_TYPE_SHAPES = {
    'ストレート': 'ellipse', 'カーブ': 'rectangle', 'スライダー': 'triangle',
    'フォーク': 'diamond', 'チェンジアップ': 'star', 'その他': 'ellipse'
}

# --- ヘルパー関数 ---
def draw_shape(draw_obj, shape, x, y, size, color):
    h_size = size / 2
    if shape == 'ellipse':
        draw_obj.ellipse((x - h_size, y - h_size, x + h_size, y + h_size), fill=color, outline=color)
    elif shape == 'rectangle':
        draw_obj.rectangle((x - h_size, y - h_size, x + h_size, y + h_size), fill=color, outline=color)
    elif shape == 'triangle':
        points = [(x, y - h_size), (x - h_size, y + h_size), (x + h_size, y + h_size)]
        draw_obj.polygon(points, fill=color, outline=color)
    elif shape == 'diamond':
        points = [(x, y - h_size), (x + h_size, y), (x, y + h_size), (x - h_size, y)]
        draw_obj.polygon(points, fill=color, outline=color)
    else:
        draw_obj.ellipse((x - h_size, y - h_size, x + h_size, y + h_size), fill=color, outline=color)

# --- Streamlit アプリケーション ---
st.set_page_config(layout="wide")
st.title("⚾ 打球分析アプリ - データ閲覧")

st.sidebar.header("操作パネル")

# ### 変更 ###: hitting_data.csvを持つフォルダをチームとして認識
team_folders_with_data = sorted([
    d for d in os.listdir('.') 
    if os.path.isdir(d) and os.path.exists(os.path.join(d, DATA_FILENAME))
])

if not team_folders_with_data:
    st.warning("表示するデータを持つチームフォルダがありません。")
else:
    # フォルダ名をチーム選択のドロップダウンとして表示
    selected_team_folder = st.sidebar.selectbox("閲覧するチームを選択", team_folders_with_data)

    if selected_team_folder:
        data_path = os.path.join(selected_team_folder, DATA_FILENAME)
        try:
            hitting_df = pd.read_csv(data_path)
        except Exception as e:
            st.error(f"{data_path}の読み込みに失敗しました: {e}")
            hitting_df = pd.DataFrame() # エラーの場合は空のデータフレームを作成
        
        try:
            base_img = Image.open(BASEBALL_FIELD_IMG).resize(IMAGE_SIZE)
        except FileNotFoundError:
            st.error(f"{BASEBALL_FIELD_IMG}が見つかりません。")
            st.stop()

        st.sidebar.header("絞り込み条件")
        
        # フィルターの選択肢を動的に生成
        player_options = ["すべて"] + sorted(hitting_df['player_name'].unique().tolist())
        pitch_type_options = ["すべて"] + sorted(hitting_df['pitch_type'].unique().tolist())
        hit_type_options = ["すべて"] + sorted(hitting_df['hit_type'].unique().tolist())
        
        player_filter = st.sidebar.selectbox("選手を選択", player_options)
        balls_filter = st.sidebar.selectbox("ボール", ["すべて", "0", "1", "2", "3"])
        strikes_filter = st.sidebar.selectbox("ストライク", ["すべて", "0", "1", "2"])
        pitch_type_filter = st.sidebar.selectbox("球種で絞り込み", pitch_type_options)
        hit_type_filter = st.sidebar.selectbox("打球性質で絞り込み", hit_type_options)

        # --- データフィルタリング ---
        filtered_df = hitting_df.copy()
        if player_filter != "すべて":
            filtered_df = filtered_df[filtered_df['player_name'] == player_filter]
        if balls_filter != "すべて":
            filtered_df = filtered_df[filtered_df['balls'].astype(str) == balls_filter]
        if strikes_filter != "すべて":
            filtered_df = filtered_df[filtered_df['strikes'].astype(str) == strikes_filter]
        if pitch_type_filter != "すべて":
            filtered_df = filtered_df[filtered_df['pitch_type'] == pitch_type_filter]
        if hit_type_filter != "すべて":
            filtered_df = filtered_df[filtered_df['hit_type'] == hit_type_filter]

        st.write(f"**{selected_team_folder}** のデータ - 表示件数: **{len(filtered_df)}**件")

        # --- 描画 ---
        img_to_draw = base_img.copy()
        draw = ImageDraw.Draw(img_to_draw)
        for _, row in filtered_df.iterrows():
            color = HIT_TYPE_COLORS.get(row['hit_type'], 'gray')
            shape = PITCH_TYPE_SHAPES.get(row['pitch_type'], 'ellipse')
            x, y = row['x_coord'], row['y_coord']
            draw_shape(draw, shape, int(x), int(y), 10, color)
        
        st.image(img_to_draw, use_column_width=True)
        
        if st.checkbox("フィルター結果のデータを表示"):
            st.dataframe(filtered_df)