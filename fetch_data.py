import urllib.request
import datetime

# 取得當前 UTC 時間
today_utc = datetime.datetime.utcnow()

# 利用 timedelta 減去 1 天，取得前一天的時間
yesterday_utc = today_utc - datetime.timedelta(days=1)

# 根據前一天的時間計算年份與年積日 (DOY)
yyyy = yesterday_utc.strftime("%Y")
doy = yesterday_utc.strftime("%j")

# 組合 AIUB 動態檔名與目標網址 (指向前一天的資料)
filename = f"COD0OPSRAP_{yyyy}{doy}0000_01D_01H_GIM.INX.gz"
url = f"https://www.aiub.unibe.ch/download/CODE/{filename}"

# 統一儲存為固定檔名，讓實驗室端的 MATLAB 每天抓同一個網址即可
save_path = "latest_GIM.inx.gz"

print(f"準備從 {url} 下載前一日的觀測資料...")
try:
    urllib.request.urlretrieve(url, save_path)
    print("下載成功！檔案已準備就緒。")
except Exception as e:
    print(f"下載失敗: {e}")
