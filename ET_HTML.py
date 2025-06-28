import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import japanize_matplotlib
import plotly.graph_objects as go

df = pd.read_csv("EarthquakeData.csv", skiprows=2, header=None, names=["日時", "震央地名", "深さ", "マグニチュード", "震度"])

filtered_df = df[df["震央地名"] == "トカラ列島近海"].copy()

filtered_df["日時"] = filtered_df["日時"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"))
filtered_df = filtered_df[filtered_df["日時"] >= datetime(2025, 6, 21)]
filtered_df.sort_values("日時", inplace=True) #inplace=Trueでdfに並び替えが保存

filtered_df["マグニチュード"] = pd.to_numeric(filtered_df["マグニチュード"], errors='coerce')
filtered_df = filtered_df.dropna(subset=["マグニチュード"])
filtered_df["logE"] = 1.5 * filtered_df["マグニチュード"] + 11.8
filtered_df["E"] = 10 ** filtered_df["logE"]
filtered_df["累積E"] = filtered_df["E"].cumsum()
filtered_df["累積N"] = np.arange(1, len(filtered_df) + 1)
"""
fig, ax1 = plt.subplots(figsize=(10, 6))

ax1.step(filtered_df["日時"], filtered_df["累積E"], where="post", color="k", label="累積地震エネルギー")
ax1.set_xlabel("日時")
ax1.set_ylabel("エネルギー[erg]", color="k")
#ax1.set_title("E-T図")
ax1.tick_params(axis="y", labelcolor='k') #y軸の目盛りのセットアップ
ax1.grid(True, which='both', linestyle="--", alpha=0.5)

ax2 = ax1.twinx()
ax2.step(filtered_df["日時"], filtered_df["累積N"], where="post", color="r", label="累積地震回数")
ax2.set_ylabel("累積地震回数[回]", color="red")
ax2.tick_params(axis="y", labelcolor="r")

plt.title("累積地震エネルギーと累積地震回数")

lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
plt.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper left")

plt.tight_layout()
plt.show()
"""

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=filtered_df["日時"], y=filtered_df["累積E"],
    mode='lines',
    name='累積地震エネルギー[erg]',
    line=dict(shape='hv', color="black"),
    yaxis="y1"
))

fig.add_trace(go.Scatter(
    x=filtered_df["日時"], y=filtered_df["累積N"],
    mode='lines+markers',
    name="累積地震回数[回]",
    line=dict(shape='hv', color="red"),
    yaxis="y2"
))

fig.update_layout(
    title='***',
    font=dict(size=14),
    xaxis=dict(title='日時'),
    yaxis=dict(title="エネルギー[erg]"),
    yaxis2=dict(title="地震回数[回]", overlaying='y', side="right"),
    legend=dict(x=0.01, y=1.15, orientation="h"),
    margin=dict(l=60, r=60, t=60, b=40),
    hovermode="x unified"
)

fig.write_html("plot/et_graph.html", include_plotlyjs="cdn")