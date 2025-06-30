import pandas as pd
import plotly.graph_objects as go
import plotly.subplots as sp
import os
import glob #ファイルパターン
import re #正規表現

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

data_all = []

for file in sorted(file_list):
    df = pd.read_csv(file)
    df = df[df["震央地名"] == "トカラ列島近海"]
    if os.path.basename(file).startswith("202506"): #ネットから生データとってくるので、処理必要
        df = df[df["地震の発生日"] >= "2025/06/21"]
    df['lat'] = df['緯度'].apply(dms_to_deg)
    df['lon'] = df['経度'].apply(dms_to_deg)
    df['file_id'] = os.path.basename(file)
    data_all.append(df)

df_all = pd.concat(data_all)

#フィルター
#df_all = df_all[df_all['mag'] >= 4.0]
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
"""

"""
# --- ヒートマップ用ヒストグラム ---
lon_bins = np.linspace(lon_min, lon_max, 100)
lat_bins = np.linspace(lat_min, lat_max, 100)
H, xedges, yedges = np.histogram2d(df_all['lon'], df_all['lat'], bins=[lon_bins, lat_bins])
heatmap = H.T

# --- 地図 (ax_xy) の描画 ---
ax_xy = fig.add_subplot(gs[0, 0], projection=ccrs.PlateCarree())
ax_xy.set_title("震源分布図 (緯度・経度)")
ax_xy.coastlines(resolution='10m')
ax_xy.add_feature(cfeature.BORDERS, linestyle=':')
ax_xy.add_feature(cfeature.LAND, edgecolor='k', facecolor='none')

# ★ 震央密度ヒートマップの重ね描き
mesh = ax_xy.pcolormesh(xedges, yedges, heatmap, cmap='Reds', alpha=0.6, transform=ccrs.PlateCarree())

# 地図にデータプロット（元のscatter）
for file in df_all['file_id'].unique():
    sub = df_all[df_all['file_id'] == file]
    ax_xy.scatter(sub['lon'], sub['lat'], s=sub['mag']**3, edgecolors=sub['color'].iloc[0],
                  facecolors='none', label=file, transform=ccrs.PlateCarree())

# 範囲・グリッドなど（既存のまま）
ax_xy.set_extent([lon_min, lon_max, lat_min, lat_max])
gl = ax_xy.gridlines(draw_labels=True)
gl.top_labels = False
gl.right_labels = False

# ★ カラーバー追加（任意）
cbar = plt.colorbar(mesh, ax=ax_xy, orientation='vertical', shrink=0.7, pad=0.02)
cbar.set_label("震央密度")
"""
"""
plt.tight_layout()
plt.show()

"""
n = len(data_all)
cols = 3
rows = (n + cols - 1) // cols

specs_all_geo = [[{"type": "geo"}] * cols for _ in range(rows)]

fig = sp.make_subplots(rows=rows, cols=cols, subplot_titles=[df['file_id'].iloc[0] for df in data_all],
                       specs=specs_all_geo)

lon_range = [129.0, 129.5]
lat_range = [29.0, 29.4]

for i, df in enumerate(data_all):
    r = i // cols + 1 #整数除算
    c = i % cols + 1
    fig.add_trace(
        go.Scattergeo(
            lon=df["lon"],
            lat=df["lat"],
            mode="markers",
            marker=dict(size=6, line=dict(width=1, color='black')),
            name=df["file_id"].iloc[0],
            showlegend=False
        ),
        row=r, col=c
    )

    fig.update_geos(
        #scope='asia',
        resolution=50,
        showcountries=False,
        showland=True,
        landcolor='LightGreen',
        showocean=True,
        oceancolor="LightBlue",
        lonaxis=dict(range=lon_range),
        lataxis=dict(range=lat_range)
        #fitbounds="locations"
    , row=r, col=c)

fig.update_layout(
    height=300 * rows,
    width=1000,
    title_text="地震の位置",
    showlegend=False
)

fig.write_html("plot/xy_pastsepa_graph.html")