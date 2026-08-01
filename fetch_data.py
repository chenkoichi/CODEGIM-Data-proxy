import urllib.request
import urllib.error
import datetime
import os

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
    # 預防性備案：若無參數傳入，則預設抓取前一日資料
    today_utc = datetime.datetime.utcnow()
    yesterday_utc = today_utc - datetime.timedelta(days=1)
    yyyy = yesterday_utc.strftime("%Y")
    yy = yesterday_utc.strftime("%y")
    mm = yesterday_utc.strftime("%m")
    doy = yesterday_utc.strftime("%j")
    print(f"無參數傳入，自動下載前一日 {yyyy} 年 DOY {doy} 的資料。")

# ==========================================
# 2. 定義多檔案下載任務清單
# ==========================================
download_tasks = [
    {
        "name": "GIM (電離層網格)",
        "save_path": "latest_GIM.inx.gz",
        "url_list": [
            f"https://www.aiub.unibe.ch/download/CODE/{yyyy}/COD0OPSFIN_{yyyy}{doy}0000_01D_01H_GIM.INX.gz",
            f"https://www.aiub.unibe.ch/download/CODE/COD0OPSRAP_{yyyy}{doy}0000_01D_01H_GIM.INX.gz"
        ]
    },
    {
        "name": "SP3 (精密軌道)",
        "save_path": "latest_ORB.sp3.gz",
        "url_list": [
            f"https://www.aiub.unibe.ch/download/CODE/{yyyy}/COD0OPSFIN_{yyyy}{doy}0000_01D_05M_ORB.SP3.gz",
            f"https://www.aiub.unibe.ch/download/CODE/COD0OPSRAP_{yyyy}{doy}0000_01D_05M_ORB.SP3.gz"
        ]
    },
    {
        "name": "P1P2 (DCB 儀器偏差)",
        "save_path": "latest_P1P2.DCB.Z",
        "url_list": [
            f"https://www.aiub.unibe.ch/download/CODE/{yyyy}/P1P2{yy}{mm}.DCB.Z",
            f"https://www.aiub.unibe.ch/download/CODE/{yyyy}/P1P2{yy}{mm}_ALL.DCB.Z"
        ]
    },
    {
        "name": "P1C1 (DCB 儀器偏差)",
        "save_path": "latest_P1C1.DCB.Z",
        "url_list": [
            f"https://www.aiub.unibe.ch/download/CODE/{yyyy}/P1C1{yy}{mm}.DCB.Z",
            f"https://www.aiub.unibe.ch/download/CODE/{yyyy}/P1C1{yy}{mm}_ALL.DCB.Z"
        ]
    },
    {
        "name": "Dst Index (地磁指數)",
        "save_path": "dst_index.html",
        "url_list": [
            f"https://wdc.kugi.kyoto-u.ac.jp/dst_realtime/{yyyy}{mm}/dst_index.html"
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
    print(f"\n[{task['name']}] 準備下載，目標儲存為: {task['save_path']}")
    task_success = False
    
    for url in task["url_list"]:
        print(f" -> 嘗試連線: {url}")
        try:
            req = urllib.request.Request(url, headers=req_headers)
            with urllib.request.urlopen(req, timeout=30) as response, open(task['save_path'], 'wb') as out_file:
                out_file.write(response.read())
            print("   [成功] 檔案下載完畢！")
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
