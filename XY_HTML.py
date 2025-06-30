import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import os
import glob #ファイルパターン
import re #正規表現
import japanize_matplotlib
import matplotlib.gridspec as gridspec
import seaborn as sns
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def dms_to_deg(dms_str):
    match = re.match(r"(\d+)°(\d+(?:\.\d+)?)′([NSWE])", dms_str)
    if not match:
        return None
    degrees, minutes, direction = match.groups()
    decimal = float(degrees) + float(minutes) / 60
    if direction in ['S', 'W']:
        decimal *= -1
    return decimal

file_list = [f for f in glob.glob("*.csv") if re.fullmatch(r"\d{6}\.csv", os.path.basename(f))]
#colors = plt.colormaps.get_cmap('tab10', len(file_list))
#colors = plt.colormaps['tab10']
color_list=['red', 'blue', 'green', 'orange', 'purple', 'brown', 'cyan', 'magenta', 'gray', 'black']

data_all = []


for idx, file in enumerate(sorted(file_list)):
    df = pd.read_csv(file)
    df = df[df["震央地名"] == "トカラ列島近海"]
    if os.path.basename(file).startswith("202506"): #ネットから生データとってくるので、処理必要
        df = df[df["地震の発生日"] >= "2025/06/21"]
    df['lat'] = df['緯度'].apply(dms_to_deg)
    df['lon'] = df['経度'].apply(dms_to_deg)
    df['depth_km'] = pd.to_numeric(df['深さ'].str.replace(' km', '').replace('ごく浅い', '0'), errors='coerce')
    df['mag'] = pd.to_numeric(df['Ｍ'], errors='coerce')
    df = df.dropna(subset=["mag", "lat", "lon", "depth_km"])
    df['file_id'] = file
    df['color'] = color_list[idx % len(color_list)]
    data_all.append(df)

df_all = pd.concat(data_all, ignore_index=True)

#フィルター
#df_all = df_all[df_all['mag'] >= 4.0]

fig = make_subplots(
    rows=2, cols=2,
    column_widths=[0.7, 0.3],
    row_heights=[0.7, 0.3],
    specs=[[{"type": "scattergeo"}, {"type": "scatter"}],
           [{"type": "scatter"}, None]],
    subplot_titles=["震源分布図（X-Y）", "断面図（D-Y)", "断面図（X-D）"]
)

for df in data_all:
    fig.add_trace(
        go.Scattergeo(
            lon=df["lon"],
            lat=df["lat"],
            text=[f"M{m:.1f}<br>深さ:{d}km" for m, d in zip(df["mag"], df["depth_km"])],
            mode='markers',
            marker=dict(
                size=df["mag"] ** 2,
                color=df["color"].iloc[0],
                line=dict(width=1, color='black')
            ),
            name=df["file_id"].iloc[0]
        ),
        row=1, col=1
    )

for df in data_all:
    fig.add_trace(
        go.Scatter(
            x=df["depth_km"],
            y=df["lat"],
            mode='markers',
            marker=dict(size=df["mag"] ** 2, color=df["color"].iloc[0], line=dict(width=1, color='black')),
            name=df["file_id"].iloc[0],
            showlegend=False
        ),
        row=1, col=2
    )

for df in data_all:
    fig.add_trace(
        go.Scatter(
            x=df["lon"],
            y=df["depth_km"],
            
            mode='markers',
            marker=dict(size=df["mag"] ** 2, color=df["color"].iloc[0], line=dict(width=1, color='black')),
            name=df["file_id"].iloc[0],
            showlegend=False
        ),
        row=2, col=1
    )

fig.update_geos(
    projection_type='mercator',
    showland=True, landcolor="rgb(230, 230, 230)",
    showcoastlines=True, coastlinecolor='gray',
    showcountries=True,
    lataxis_range=[df_all["lat"].min() - 0.2, df_all["lat"].max() + 0.2],
    lonaxis_range=[df_all["lon"].min() - 0.2, df_all["lon"].max() + 0.2]
)

fig.update_yaxes(title_text="緯度", row=1, col=2)
fig.update_xaxes(title_text="深さ[km]", row=1, col=2)
fig.update_xaxes(title_text="経度", row=2, col=1)
fig.update_yaxes(title_text="深さ[km]", row=2, col=1, autorange='reversed')

fig.update_layout(
    title="地震分布図（地図＋断面）",
    height=800,
    width=1000,
    legend_title="年月",
    template="plotly_white"

)

fig.write_html("plot/xy_graph.html")

"""
fig = plt.figure(figsize=(10, 10))
gs = gridspec.GridSpec(3, 3, height_ratios=[3, 0.2, 1], width_ratios=[3, 0.2, 1], hspace=0.1, wspace=0.1)
#gs = gridspec.GridSpec(nrows=2, ncols=2, height_ratios=[3, 1], width_ratios=[3, 1], hspace=0.05, wspace=0.05)
#gs = gridspec.GridSpec(2, 2, width_ratios=[4, 1.2], height_ratios=[4, 1.2], hspace=0.05, wspace=0.05)


# 中央：x-y 地図（経度-緯度）
ax_xy = fig.add_subplot(gs[0, 0], projection=ccrs.PlateCarree())
ax_xy.set_title("震源分布図 (緯度・経度)")
ax_xy.coastlines(resolution='10m')
ax_xy.add_feature(cfeature.BORDERS, linestyle=':')
ax_xy.add_feature(cfeature.LAND, edgecolor='k', facecolor='none')

# 地図にデータプロット
for file in df_all['file_id'].unique():
    sub = df_all[df_all['file_id'] == file]
    ax_xy.scatter(sub['lon'], sub['lat'], s=sub['mag']**3, edgecolors=sub['color'].iloc[0],
                  facecolors='none', label=file, transform=ccrs.PlateCarree())

# 地図の範囲とグリッド
lon_min, lon_max = df_all['lon'].min()-0.2, df_all['lon'].max()+0.2
lat_min, lat_max = df_all['lat'].min()-0.2, df_all['lat'].max()+0.2
ax_xy.set_extent([lon_min, lon_max, lat_min, lat_max])
gl = ax_xy.gridlines(draw_labels=True)
gl.top_labels = False
gl.right_labels = False

# 下：x-z 断面図（経度-深さ）
ax_xz = fig.add_subplot(gs[2, 0])
ax_xz.set_title("断面図 (経度-深さ)")
for file in df_all['file_id'].unique():
    sub = df_all[df_all['file_id'] == file]
    ax_xz.scatter(sub['lon'], sub['depth_km'], s=sub['mag']**3,
                  edgecolors=sub['color'].iloc[0], facecolors='none', label=file)
ax_xz.set_xlim(lon_min, lon_max)
ax_xz.set_xlabel("経度")
ax_xz.set_ylabel("深さ [km]")
ax_xz.invert_yaxis()
ax_xz.grid(True)

# 右：y-z 断面図（深さ-緯度）
ax_yz = fig.add_subplot(gs[0, 2])
ax_yz.set_title("断面図 (深さ-緯度)")
for file in df_all['file_id'].unique():
    sub = df_all[df_all['file_id'] == file]
    ax_yz.scatter(sub['depth_km'], sub['lat'], s=sub['mag']**3,
                  edgecolors=sub['color'].iloc[0], facecolors='none', label=file)
ax_yz.set_ylim(lat_min, lat_max)
ax_yz.set_xlabel("深さ [km]")
ax_yz.set_ylabel("緯度")
#ax_yz.invert_xaxis()  # 深いほうを右にするなら削除
ax_yz.grid(True)

# 凡例を別途表示（必要なら）
ax_xy.legend(fontsize='small', loc='lower right')



plt.tight_layout()
plt.show()



# 描画設定（横3列）
n = len(data_all)
cols = 3
rows = (n + cols - 1) // cols
fig, axes = plt.subplots(rows, cols, figsize=(5*cols, 5*rows))
axes = axes.flatten()

# 範囲固定
lon_min, lon_max = 129.0, 129.5
lat_min, lat_max = 29.0, 29.4

# 各サブプロットにKDE描画
for i, df in enumerate(data_all):
    ax = axes[i]
    if not df.empty:
        sns.kdeplot(
            data=df, x="lon", y="lat",
            fill=True, cmap="Reds", bw_adjust=0.3, alpha=0.6,
            thresh=0.05, ax=ax
        )
        ax.scatter(df['lon'], df['lat'], s=10, facecolors='none', edgecolors='k', alpha=0.4)
        ax.set_title(f"{df['file_id'].iloc[0]}")
        ax.set_xlim(lon_min, lon_max)
        ax.set_ylim(lat_min, lat_max)
        ax.set_xlabel("経度")
        ax.set_ylabel("緯度")
    else:
        ax.set_visible(False)

# 余白のサブプロットを非表示
for j in range(i + 1, len(axes)):
    axes[j].set_visible(False)

plt.tight_layout()
plt.show()
"""