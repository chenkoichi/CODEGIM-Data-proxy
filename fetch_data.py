import urllib.request
import urllib.error
import datetime
import sys

# 1. 取得前一日的 UTC 時間，並計算年份與年積日 (DOY)
today_utc = datetime.datetime.utcnow()
yesterday_utc = today_utc - datetime.timedelta(days=1)

yyyy = yesterday_utc.strftime("%Y")
doy = yesterday_utc.strftime("%j")

# 2. 組合 FIN (最終版) 與 RAP (快速版) 的檔名
gimfn_fin = f"COD0OPSFIN_{yyyy}{doy}0000_01D_01H_GIM.INX.gz"
gimfn_rap = f"COD0OPSRAP_{yyyy}{doy}0000_01D_01H_GIM.INX.gz"

# 3. 建立下載優先清單 (完全對應 MATLAB 的 fallback 邏輯)
download_list = [
    # 優先嘗試：FIN 檔案 (位於年份資料夾下)
    f"https://www.aiub.unibe.ch/download/CODE/{yyyy}/{gimfn_fin}",
    
    # 備援嘗試：RAP 檔案 (位於 CODE 根目錄下)
    f"https://www.aiub.unibe.ch/download/CODE/{gimfn_rap}"
]

# 設定 GitHub 轉運站的統一儲存檔名
save_path = "latest_GIM.inx.gz"
download_success = False

# 設定 User-Agent 偽裝與 MATLAB 腳本保持一致，避免被伺服器阻擋
req_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'
}

print(f"開始尋找並下載 {yyyy} 年 DOY {doy} 的 GIM 檔案...")

# 4. 執行下載迴圈
for url in download_list:
    print(f" -> 嘗試下載: {url}")
    try:
        # 建立帶有標頭的請求
        req = urllib.request.Request(url, headers=req_headers)
        
        # 執行下載，設定 Timeout 為 30 秒
        with urllib.request.urlopen(req, timeout=30) as response, open(save_path, 'wb') as out_file:
            out_file.write(response.read())
            
        print("   [成功] 檔案下載完畢！")
        download_success = True
        break  # 成功取得檔案，立即跳出迴圈

    except urllib.error.URLError as e:
        print(f"   [失敗] 無法取得此檔案: {e.reason}")
    except Exception as e:
        print(f"   [失敗] 發生未預期的錯誤: {e}")

# 5. 例外處理：若所有路徑皆失敗
if not download_success:
    print("所有下載嘗試皆失敗，無法取得 FIN 或 RAP 檔案！請確認該 DOY 日期是否已有資料。")
    sys.exit(1) # 強制回傳錯誤碼 1，讓 GitHub Actions 面板亮紅燈，方便你第一時間察覺異常
