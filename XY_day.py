import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

df = pd.read_csv("EarthquakeData_latlon.csv", parse_dates=["地震の発生日時"]) #datetime型で読み込む列の指定

df = df[df["地震の発生日時"] >= pd.to_datetime("2025-06-21")]

df["date"] = df["地震の発生日時"].dt.date #月日だけの列

grouped = df.groupby("date")

fig = go.Figure()

frames = []
slider_steps = []

for i, (date, group) in enumerate(sorted(grouped)): #groupにはその日の地震リストが入る
    group = group.dropna(subset=["マグニチュード", "緯度", "経度", "深さ"])
    scatter = go.Scattermapbox(
        lon=group["経度"],
        lat=group["緯度"],
        mode="markers",
        marker=dict(
            size=group["マグニチュード"] * 4,
            color=group["深さ"],
            cmin=0, 
            cmax=30,
            colorscale="Viridis",
            colorbar=dict(title="深さ（km）"),
            #line=dict(width=1, color="black"),
            opacity=0.7,
            symbol="circle"
        ),
        text=group["震央地名"] + "<br>深さ:" + group["深さ"].astype(str) + "km",
        name=str(date)
    )

    if i == 0:
        fig.add_trace(scatter)

    frames.append(go.Frame(data=[scatter], name=str(date)))
    slider_steps.append({
        "args": [[str(date)], {"frame": {"duration": 0, "redraw": True},
                               "mode": "immediate"}],
        "label": str(date),
        "method": "animate"
    })

center_lat = df["緯度"].mean()
center_lon = df["経度"].mean()

fig.update_layout(
    title="地震の分布（緯度・経度）",
    mapbox=dict(
        style="open-street-map",
        center=dict(lat=center_lat, lon=center_lon),
        zoom=6
    ),
    margin=dict(r=0, l=0, b=100, t=40),
    updatemenus=[{
        "type": "buttons",
        "buttons": [
            {
                "label": "再生",
                "method": "animate",
                "args": [None, {"frame": {"duration": 500, "redraw": True}, "fromcurrent": True}],
            },
            {
                "label": "停止",
                "method": "animate",
                "args": [[None], {"mode": "immediate", "frame": {"duration": 0}, "transition": {"duration": 0}}],
            }
        ],
        "direction": "left",
        "pad": {"r": 10, "t": 10},
        "showactive": True,
        "x": 0.1,
        "y": 0.2,
        "xanchor": "right",
        "yanchor": "bottom"
    }],
    sliders=[{
        "active": 0,
        "pad": {"t": 50},
        "steps": slider_steps,
        "x": 0.1,
        "y": 0.1,
        "len": 0.9
    }],
    #frames=frames
)
fig.frames = frames
fig.write_html("plot/xy_day_graph.html")