import pandas as pd
import plotly.express as px

# CSV読み込み
df = pd.read_csv("EarthquakeData_latlon.csv")
df["地震の発生日時"] = pd.to_datetime(df["地震の発生日時"])

# トカラ列島近海のみ抽出し、必要な列でNaNを除去
df_tokara = df[df["震央地名"] == "トカラ列島近海"].copy()
df_tokara = df_tokara.dropna(subset=["マグニチュード", "緯度", "深さ", "地震の発生日時"])

# バブルサイズ列の作成
df_tokara["サイズ"] = df_tokara["マグニチュード"] ** 2 * 10

# 緯度基準線用の辞書
landmarks = {
    "悪石島": 29.4589,
    "小宝島": 29.2232,
}

# Plotlyで描画
fig = px.scatter(
    df_tokara,
    x="地震の発生日時",
    y="緯度",
    size="サイズ",
    color="深さ",
    color_continuous_scale="Viridis_r",
    hover_data=["マグニチュード", "深さ", "震央地名"],
    labels={"深さ": "深さ[km]", "緯度": "緯度", "地震の発生日時": "発生日時"},
    title="トカラ列島近海の地震分布（日時-緯度）"
)

# 緯度の島ラベル
for name, lat in landmarks.items():
    fig.add_hline(
        y=lat,
        line_dash="dash",
        line_color="red",
        annotation_text=name,
        annotation_position="top left",
        annotation_font_size=12,
        opacity=0.8
    )

# 深さのカラーバーを反転
fig.update_coloraxes(reversescale=True)

# レイアウト
fig.update_layout(
    xaxis=dict(title="地震の発生日時", tickformat="%m-%d<br>%H:%M"),
    yaxis_title="緯度"
)

# HTML出力
fig.write_html("plot/xt_graph.html")
