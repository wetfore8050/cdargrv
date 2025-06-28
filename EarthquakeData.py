from datetime import datetime, timedelta
from LatestEarthquakeData import run_code2
from PastEarthquakeData import run_code1
import pandas as pd
import os
import re
import shutil

#import LatestEarthquakeData
downloads_dir = "downloads_csv"
if os.path.exists(downloads_dir):
    for filename in os.listdir(downloads_dir):
        file_path = os.path.join(downloads_dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path): #ファイルであるかどうか
                os.remove(file_path)
            elif os.path.isdir(file_path): #フォルダなら
                shutil.rmtree(file_path)
        except Exception as e:
            print("削除不可")

START_DATE = "2024-07-20"
START_TIME = "00:00"

#END_DATE = "2025-06-26"
#END_TIME = "23:59"

now = datetime.now()
print(f"now: {now}")

END_DATE = now.strftime("%Y-%m-%d")
END_TIME = now.strftime("%H:%M")

five_days_ago_midnight = (now - timedelta(days=5)).replace(hour=0, minute=0, second=0, microsecond=0) #replaceで別の時間に置き換え
print(five_days_ago_midnight)

start_dt = datetime.strptime(f"{START_DATE} {START_TIME}", "%Y-%m-%d %H:%M")
end_dt = datetime.strptime(f"{END_DATE} {END_TIME}", "%Y-%m-%d %H:%M")

if end_dt < five_days_ago_midnight:
    print("コード1のみ実行")
    run_code1(START_DATE, START_TIME, END_DATE, END_TIME)
    
elif start_dt > five_days_ago_midnight:
    print("コード2のみ実行")
    run_code2()

else:
    print("コード1とコード2の両方を実行")
    one_minute_before_mid = five_days_ago_midnight - timedelta(minutes=1)

    mid_date = one_minute_before_mid.strftime("%Y-%m-%d")
    mid_time = one_minute_before_mid.strftime("%H:%M")
    run_code1(START_DATE, START_TIME, mid_date, mid_time)
    run_code2()

def convert_to_decimal(coord_str):
    if not isinstance(coord_str, str):
        print(f"非文字列: {coord_str}")
        return None
    
    coord_str = coord_str.strip()
    pattern = r"(\d+)°(\d+(?:\.\d+)?)[′´']([NSEW])"
    match = re.match(pattern, coord_str) #d+で整数　#r文字列でバックスラッシュを文字列
    #print(match)
    if not match or len(match.groups()) != 3:
        print(f"[マッチ失敗]: {coord_str}")
        return None
    deg, minute, direction = match.groups()
    decimal = float(deg) + float(minute) / 60
    if direction in ["S", "W"]:
        decimal = -decimal
    return round(decimal, 4)

def clean_depth(depth_str):
    if isinstance(depth_str, str): #isinstanceは第1引数が第2引数の型に一致してるかチェック
        if depth_str == "ごく浅い":
            return 0
        return int(depth_str.replace("km", "").replace(" ", "").replace("　", "")) #全角半角スペースも削除
    return int(depth_str) if str(depth_str).isdigit else None

def convert_datetime_last(jp_dt_str):
    return datetime.strptime(jp_dt_str, "%Y年%m月%d日%H時%M分")

def convert_datetime_past(date_str, time_str):
    return datetime.strptime(f"{date_str} {time_str.split('.')[0]}", "%Y/%m/%d %H:%M:%S")

def make_combined_csv():
    #global five_days_ago_midnight
    files = sorted([f for f in os.listdir("downloads_csv") if f.startswith("earthquake_") and f.endswith(".csv")],
                   key=lambda x: int(re.findall(r'\d+', x)[0]))
    all_data = []
    latlon_data = []

    for f in files:
        path = os.path.join("downloads_csv", f)
        if f == "earthquake_0.csv":
            df = pd.read_csv(path, header=None)
            df = df.dropna(how='any') #any=1つでもnanで消去
            df = df[df[0].str.contains("年" ,na=False)] #年を含む列のみ残す

            df_clean = pd.DataFrame()
            df_clean["地震の発生日時"] = df[0].apply(convert_datetime_last)
            df_clean["震央地名"] = df[1]
            df_clean["深さ"] = df[2].apply(clean_depth)
            df_clean["マグニチュード"] = pd.to_numeric(df.iloc[:, 3], errors='coerce')
            df_clean["震度"] = df[4]

            df_filtered = df_clean[df_clean["地震の発生日時"] >= five_days_ago_midnight].copy()

            all_data.append(df_filtered)
        else:
            df = pd.read_csv(path)
            df.replace("不明", pd.NA, inplace=True) #inplaceは新しく置換

            df_clean = pd.DataFrame()
            df_clean["地震の発生日時"] = df.apply(lambda row: convert_datetime_past(str(row[0]), str(row[1])), axis=1)
            df_clean["震央地名"] = df.iloc[:, 2]
            df_clean["深さ"] = df.iloc[:, 5].apply(clean_depth)
            df_clean["マグニチュード"] = pd.to_numeric(df.iloc[:, 6], errors='coerce')
            df_clean["震度"] = df.iloc[:, 7]
            df_clean["緯度"] = df.iloc[:, 3].apply(convert_to_decimal)
            df_clean["経度"] = df.iloc[:, 4].apply(convert_to_decimal)

            all_data.append(df_clean[["地震の発生日時", "震央地名", "深さ", "マグニチュード", "震度"]])
            latlon_data.append(df_clean)

    #os.makedirs("data", exist_ok=True)

    if all_data:
        pd.concat(all_data, ignore_index=True).to_csv("EarthquakeData.csv", index=False, encoding='utf-8-sig') #ただインデックス降りなおすためのconcat
        print("EarthquakeData.csv完成")
    
    if latlon_data:
        pd.concat(latlon_data, ignore_index=True).to_csv("EarthquakeData_latlon.csv", index=False, encoding='utf-8-sig')
        print("EarthquakeData_latlon.csv完成")

make_combined_csv()