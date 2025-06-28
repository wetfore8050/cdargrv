from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.alert import Alert
import pandas as pd
import time
import os
from datetime import datetime, timedelta

#START_DATE = "2025-01-20"
#START_TIME = "00:00"
#END_DATE = "2025-06-26"
#END_TIME = "23:59"

def run_code1(start_date, start_time, end_date, end_time):
    DOWNLOAD_DIR = os.path.abspath("downloads_csv") #このディレクトリの配下の絶対パス取得

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    #options = webdriver.ChromeOptions()
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_DIR, #ダウンロード先
        "download.prompt_for_download": False, #確認ダイアログ無効化
        "download.directory_upgrade": True, #上書き可
        "safebrowsing.enabled": True
    })
    chrome_options.add_argument('--headless')  # Headless Chrome用
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')  # GPU関連エラー対策（Linuxで安定）
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 20)

    url = "https://www.data.jma.go.jp/eqdb/data/shindo/index.html"
    driver.get(url)

    time.sleep(5)

    file_counter = 1

    def set_search_conditions(s_date, s_time, e_date, e_time):
        print(s_date, s_time, e_date, e_time)
        #条件を指定して検索をクリック
        wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/header/div/div[3]/button[4]"))).click() #タプルで渡すので括弧が2つ
        time.sleep(1)

        start_input = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/nav[1]/div/div/div[3]/div[2]/div[2]/div/div/div/div[3]/input")))
        end_input = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/nav[1]/div/div/div[3]/div[3]/div[2]/div/div/div/div[3]/input")
        
        driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input'));", start_input, s_date)
        driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input'));", end_input, e_date)
        """
        start_input.clear()
        end_input.clear()
        time.sleep(0.5)
        start_input.send_keys(s_date)
        end_input.send_keys(e_date)
        time.sleep(0.5)
        """

        start_time_input = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/nav[1]/div/div/div[3]/div[2]/div[3]/div/div/div/div[3]/input")
        end_time_input = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/nav[1]/div/div/div[3]/div[3]/div[3]/div/div/div/div[3]/input")
        
        driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input'));", start_time_input, s_time)
        driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input'));", end_time_input, e_time)

        """
        start_time_input.clear()
        end_time_input.clear()
        time.sleep(0.5)
        start_time_input.send_keys(s_time)
        end_time_input.send_keys(e_time)
        time.sleep(0.5)
        """

        # 検証: 実際にフォームに入力された値をログ出力
        print("[Form filled]")
        print("start_date (input):", start_input.get_attribute("value"))
        print("end_date (input):  ", end_input.get_attribute("value"))
        print("start_time (input):", start_time_input.get_attribute("value"))
        print("end_time (input):  ", end_time_input.get_attribute("value"))


    def run_search_and_download():
        print(f"[Search and Download] Using conditions:")
        print(f"start: {start_date} {start_time} → end: {current_end_date} {current_end_time}")


        nonlocal file_counter

        before_files = set(os.listdir(DOWNLOAD_DIR))

        #検索
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/nav[1]/div/div/div[2]/button[1]").click()
        time.sleep(5)



        wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/header/div/div[3]/button[2]"))).click()
        time.sleep(2)

        csv_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/nav[3]/div/div/div[3]/button")))
        csv_button.click()

        ok_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[9]/div[2]/div/button[1]")))
        ok_button.click()

        Alert(driver).accept()
        time.sleep(1)

        downloaded = None
        
        for _ in range(30):
            time.sleep(1)
            after_files = set(os.listdir(DOWNLOAD_DIR))
            new_files = after_files - before_files
            csv_files = [f for f in new_files if f.endswith(".csv")]
            if csv_files:
                downloaded = csv_files[0]
                break
        if not downloaded:
            raise Exception("DONT CSV")
        
        old_path = os.path.join(DOWNLOAD_DIR, downloaded)
        new_filename = f"earthquake_{file_counter}.csv"
        new_path = os.path.join(DOWNLOAD_DIR, new_filename)
        os.rename(old_path, new_path)
        print(f'保存:{new_filename}')

        file_counter += 1

        try:
            message_elem = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/main/div/div/div[3]/ul/li[2]")
            if "上限を超えました" in message_elem.text:
                over_limit = True
            else:
                over_limit = False
        except:
            over_limit = False

        return over_limit, new_path

    def get_prev_endtime(csv_path):
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        last_row = df.iloc[-1]
        date_str = last_row[0]
        time_str = last_row[1]

        dt_str = f"{date_str} {time_str[:5]}"
        dt = datetime.strptime(dt_str, "%Y/%m/%d %H:%M")
        new_end_time = dt - timedelta(minutes=1)
        return new_end_time.strftime("%Y-%m-%d"), new_end_time.strftime("%H:%M")

    #driver.quit()

    current_end_date = end_date
    current_end_time = end_time

    while True:
        set_search_conditions(start_date, start_time, current_end_date, current_end_time)
        over_limit, csv_file_path = run_search_and_download()

        if not over_limit:
            print("全件取得完了")
            break

        print("上限超え再検索")
        current_end_date, current_end_time = get_prev_endtime(csv_file_path)

    driver.quit()