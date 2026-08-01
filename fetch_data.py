import urllib.request
import urllib.error
import datetime
import os
import glob

# ==========================================
# 0. 清理舊檔案，確保轉運站不囤積歷史資料
# ==========================================
cleanup_patterns = ["*.gz", "*.Z", "*.sp3", "*.DCB", "*.html"]
for pattern in cleanup_patterns:
    for old_file in glob.glob(pattern):
        try:
            os.remove(old_file)
        except OSError:
            pass

# ==========================================
# 1. 接收 MATLAB 傳遞的參數
# ==========================================
input_year = os.environ.get("TARGET_YEAR")
input_doy = os.environ.get("TARGET_DOY")

if input_year and input_doy:
    yyyy = input_year
    doy = input_doy.zfill(3)
    target_date = datetime.datetime.strptime(f"{yyyy}-{doy}", "%Y-%j")
    yy = target_date.strftime("%y")
    mm = target_date.strftime("%m")
    print(f"啟動 API 觸發模式：指定下載 {yyyy} 年 DOY {doy} 的資料。")
else:
    today_utc = datetime.datetime.utcnow()
    yesterday_utc = today_utc - datetime.timedelta(days=1)
    yyyy = yesterday_utc.strftime("%Y")
    yy = yesterday_utc.strftime("%y")
    mm = yesterday_utc.strftime("%m")
    doy = yesterday_utc.strftime("%j")
    print(f"無參數傳入，自動下載前一日 {yyyy} 年 DOY {doy} 的資料。")

# ==========================================
# 2. 定義多檔案下載任務清單 (產出帶有日期的專屬檔名)
# ==========================================
download_tasks = [
    {
        "name": "GIM (電離層網格)",
        "targets": [
            {"url": f"https://www.aiub.unibe.ch/download/CODE/{yyyy}/COD0OPSFIN_{yyyy}{doy}0000_01D_01H_GIM.INX.gz", "save_path": f"COD0OPS_{yyyy}{doy}_GIM.INX.gz"},
            {"url": f"https://www.aiub.unibe.ch/download/CODE/COD0OPSRAP_{yyyy}{doy}0000_01D_01H_GIM.INX.gz", "save_path": f"COD0OPS_{yyyy}{doy}_GIM.INX.gz"}
        ]
    },
    {
        "name": "SP3 (精密軌道)",
        "targets": [
            {"url": f"https://www.aiub.unibe.ch/download/CODE/{yyyy}/COD0OPSFIN_{yyyy}{doy}0000_01D_05M_ORB.SP3.gz", "save_path": f"COD0OPS_{yyyy}{doy}_ORB.SP3.gz"},
            {"url": f"https://www.aiub.unibe.ch/download/CODE/COD0OPSRAP_{yyyy}{doy}0000_01D_05M_ORB.SP3", "save_path": f"COD0OPS_{yyyy}{doy}_ORB.SP3"}
        ]
    },
    {
        "name": "P1P2 (DCB 儀器偏差)",
        "targets": [
            {"url": f"https://www.aiub.unibe.ch/download/CODE/{yyyy}/P1P2{yy}{mm}.DCB.Z", "save_path": f"P1P2_{yyyy}{doy}.DCB.Z"},
            {"url": f"https://www.aiub.unibe.ch/download/CODE/P1P2.DCB", "save_path": f"P1P2_{yyyy}{doy}.DCB"}
        ]
    },
    {
        "name": "P1C1 (DCB 儀器偏差)",
        "targets": [
            {"url": f"https://www.aiub.unibe.ch/download/CODE/{yyyy}/P1C1{yy}{mm}.DCB.Z", "save_path": f"P1C1_{yyyy}{doy}.DCB.Z"},
            {"url": f"https://www.aiub.unibe.ch/download/CODE/P1C1.DCB", "save_path": f"P1C1_{yyyy}{doy}.DCB"}
        ]
    },
    {
        "name": "Dst Index (地磁指數)",
        "targets": [
            {"url": f"https://wdc.kugi.kyoto-u.ac.jp/dst_final/{yyyy}{mm}/index.html", "save_path": f"dst_index_{yyyy}{doy}.html"},
            {"url": f"https://wdc.kugi.kyoto-u.ac.jp/dst_provisional/{yyyy}{mm}/index.html", "save_path": f"dst_index_{yyyy}{doy}.html"},
            {"url": f"https://wdc.kugi.kyoto-u.ac.jp/dst_realtime/{yyyy}{mm}/index.html", "save_path": f"dst_index_{yyyy}{doy}.html"}
        ]
    }
]

# ==========================================
# 3. 執行批次下載
# ==========================================
req_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'
}

all_tasks_successful = True
print(f"--- 開始執行 {yyyy} 年 DOY {doy} 的觀測資料批次下載 ---")

for task in download_tasks:
    print(f"\n[{task['name']}] 準備下載...")
    task_success = False
    
    for target in task["targets"]:
        url = target["url"]
        save_path = target["save_path"]
        print(f" -> 嘗試連線: {url}")
        try:
            req = urllib.request.Request(url, headers=req_headers)
            with urllib.request.urlopen(req, timeout=30) as response, open(save_path, 'wb') as out_file:
                out_file.write(response.read())
            print(f"   [成功] 檔案已下載並儲存為 {save_path}！")
            task_success = True
            break
        except urllib.error.URLError as e:
            print(f"   [失敗] 無法取得此檔案: {e.reason}")
        except Exception as e:
            print(f"   [失敗] 發生未預期的錯誤: {e}")
            
    if not task_success:
        print(f"   [警告] {task['name']} 的所有網址皆下載失敗！")
        all_tasks_successful = False

print("\n--- 批次下載作業結束 ---")
if not all_tasks_successful:
    print("部分檔案下載失敗，將繼續執行 Commit，保存已成功下載的檔案。")
else:
    print("所有檔案皆成功下載至轉運站！")
