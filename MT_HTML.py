import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import japanize_matplotlib
import plotly.graph_objects as go

df = pd.read_csv("EarthquakeData.csv", skiprows=1, header=None, names=["日時", "震央地名", "深さ", "マグニチュード", "震度"])

filtered_df = df[df["震央地名"] == "トカラ列島近海"].copy()

filtered_df["日時"] = pd.to_datetime(filtered_df["日時"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
filtered_df = filtered_df[filtered_df["日時"] >= datetime(2025, 6, 21)]
filtered_df.sort_values("日時", inplace=True) #inplace=Trueでdfに並び替えが保存

filtered_df["マグニチュード"] = pd.to_numeric(filtered_df["マグニチュード"], errors='coerce')

"""
plt.figure(figsize=(10, 5))
plt.scatter(filtered_df["日時"], filtered_df["マグニチュード"], facecolors='none', edgecolors='blue', label='地震')

for i, row in filtered_df.iterrows(): #行をループ処理
    plt.vlines(x=row["日時"], ymin=0, ymax=row["マグニチュード"], color='blue', linestyles='-')

plt.xlabel("日時")
plt.ylabel("マグニチュード")
plt.title("M-T図")
plt.tight_layout()
plt.legend()
plt.show()
"""
vline_traces = []
for _, row in filtered_df.iterrows(): #1行ずつタプルで返す 第1引数はindex
    vline_traces.append(
        go.Scatter(
            x=[row["日時"], row["日時"]],
            y=[0, row["マグニチュード"]],
            mode="lines",
            line=dict(color='blue', width=1),
            showlegend=False
        )
    )

scatter_trace = go.Scatter(
    x=filtered_df["日時"],
    y=filtered_df["マグニチュード"],
    mode="markers",
    marker=dict(symbol='circle-open', color='blue', size=8),
    name='地震'
)

fig = go.Figure(data=[scatter_trace] + vline_traces)

fig.update_layout(
    title="M-T図",
    xaxis_title='日時',
    yaxis_title='マグニチュード',
    template="plotly_white"
)

fig.write_html("plot/mt_graph.html", include_plotlyjs="cdn")