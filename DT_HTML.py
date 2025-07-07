import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# CSV読み込み
df = pd.read_csv("EarthquakeData_latlon.csv")
df["地震の発生日時"] = pd.to_datetime(df["地震の発生日時"])
df["発生日"] = df["地震の発生日時"].dt.date

# トカラ列島近海に絞る
df_tokara = df[df["震央地名"] == "トカラ列島近海"]

# 日ごとの深さと地震数
depth_by_day = df_tokara.groupby("発生日")["深さ"].apply(list)
count_by_day = df_tokara.groupby("発生日").size()

labels = depth_by_day.index.astype(str)
depths = depth_by_day.values
counts = count_by_day.values

# サブプロット作成（共有X軸、2軸Y軸）
fig = make_subplots(specs=[[{"secondary_y": True}]])

# 箱ひげ図の追加（深さ）
for i, (label, depth_list) in enumerate(zip(labels, depths)):
    fig.add_trace(
        go.Box(
            y=depth_list,
            name=label,
            boxpoints="outliers",
            marker_color='blue',
            line=dict(width=1),
            showlegend=False
        ),
        secondary_y=False
    )

# 棒グラフの追加（地震回数）
fig.add_trace(
    go.Bar(
        x=labels,
        y=counts,
        name="地震回数",
        marker_color='rgba(128,128,128,0.4)',
    ),
    secondary_y=True
)

# 軸設定・スタイル
fig.update_yaxes(title_text="深さ (km)", autorange="reversed", secondary_y=False)
fig.update_yaxes(title_text="地震回数", secondary_y=True)
fig.update_layout(
    title="トカラ列島近海における地震の深さと地震回数",
    xaxis_title="発生日",
    xaxis_tickangle=45,
    template="plotly_white",
    width=1000,
    height=600,
    margin=dict(t=60, b=100),
)

# HTMLファイルとして保存して表示可能
fig.write_html("plot/dt_graph.html", include_plotlyjs='cdn')

