import pandas as pd
import plotly.graph_objects as go
import glob
import os

csv_file = sorted(glob.glob("*.csv"))

#plt.figure(figsize=(12, 6))
fig = go.Figure()

for file in csv_file:
    basename = os.path.basename(file)
    if not basename.endswith(".csv") or not basename[:6].isdigit(): #6桁の数値であるかチェック
        continue

    df = pd.read_csv(file, header=None, names=["地震の発生日", "地震の発生時刻", "震央地名", "緯度", "経度", "深さ", "Ｍ", "最大震度"])

    df = df[df["震央地名"] == "トカラ列島近海"]

    if basename.startswith("202506"): #ネットから生データとってくるので、処理必要
        df = df[df["地震の発生日"] >= "2025/06/21"]

    if df.empty:
        continue

    df["datetime"] = pd.to_datetime(df["地震の発生日"] + " " + df["地震の発生時刻"])

    df = df.sort_values("datetime")

    t0 = df["datetime"].iloc[0]
    df["elapsed_minutes"] = (df["datetime"] - t0).dt.total_seconds() / 60

    x = df["elapsed_minutes"]
    y = list(range(1, len(df) + 1))

    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode="lines",
        line_shape='hv',
        name=basename
    ))
    #plt.step(x, y, where='post', label=os.path.basename(file))

fig.update_layout(
    title="トカラ列島近海の地震発生累積グラフ",
    xaxis_title="最初の地震からの経過時間（分）",
    yaxis_title="累積地震回数",
    legend_title="年月",
    template="plotly_white"
)

fig.write_html("plot/nt_byfile_graph.html")
"""
plt.title("トカラ列島近海の地震発生累積グラフ")
plt.xlabel("最初の地震からの経過時間（分）")
plt.ylabel("累積地震回数")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
"""