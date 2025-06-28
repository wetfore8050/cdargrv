from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import datetime
import os
import traceback


def run_code2():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')  # Headless Chrome用
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')  # GPU関連エラー対策（Linuxで安定）
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    url = "https://www.jma.go.jp/bosai/map.html#11/29.375/129.5/&elem=int&contents=earthquake_map"
    driver.get(url)

    time.sleep(5)

    try:
        quake_tab = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[9]/ul/li[2]"))
        )
        quake_tab.click()

        #table = driver.find_element(By.XPATH, "/html/body/div[9]/div/div[3]/div/table")
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[9]/div/div[3]/div/table"))
        )
        
        rows = table.find_elements(By.TAG_NAME, "tr")

        data = []
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            data.append([col.text for col in cols])
        
        df = pd.DataFrame(data)
        print(df)

        now = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"earthquake_0.csv"

        output_dir = os.path.abspath("downloads_csv")
        os.makedirs(output_dir, exist_ok=True)
        full_path = os.path.join(output_dir, filename)

        df.to_csv(full_path, index=False, encoding='utf-8-sig')
        print(f"{full_path}に保存されました。")

    except Exception as e:
        print("データ取得に失敗:", e)
        traceback.print_exc()
    finally:
        driver.quit()