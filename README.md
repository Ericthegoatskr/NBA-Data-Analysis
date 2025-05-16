# NBA 資料爬蟲與分析工具

這個專案用於爬取 NBA 官方網站上根據 robots.txt 允許的資料，並進行分析和視覺化。

## 允許爬取的資料

根據 NBA 網站的 robots.txt，以下路徑是允許爬取的：

- `/standings` - 球隊排名
- `/schedule` - 賽程表
- `/stats/help/glossary` - 數據術語表
- `/stats/draft/history` - 選秀歷史
- `/stats/help/statminimums` - 數據最低標準
- `/stats/history` - 歷史數據
- `/players` - 球員名單
- `/player/*profile` - 球員個人資料頁面
- `/team/*` - 球隊頁面（不包括球隊賽程表）

## 專案結構

專案包含以下主要程式：

### 資料爬蟲程式

1. **基本 HTML 爬蟲** (`nba_scraper.py`) - 爬取 NBA 網站的 HTML 頁面並保存
2. **進階 API 爬蟲** (`nba_advanced_scraper.py`) - 直接爬取 NBA 的 API 並提取 JSON 資料
3. **特定球員爬蟲** (`player_specific_scraper.py`) - 爬取特定球員的詳細資料與統計數據

### 資料分析程式

1. **NBA 數據分析工具** (`nba_data_analyzer.py`) - 分析爬取的基本資料並生成分析報告與圖表
2. **球員數據分析工具** (`player_specific_analyzer.py`) - 針對特定球員的數據進行深入分析

### 球員比較工具

1. **球員 ID 比較工具** (`player_comparison.py`) - 使用球員 ID 直接比較兩名球員的數據與表現
2. **球員名稱比較工具** (`player_name_comparison.py`) - 通過球員名稱搜尋並比較兩名球員

## 安裝與使用

### 1. 安裝必要套件

```bash
pip install -r requirements.txt
```

### 2. 執行基本爬蟲

```bash
python nba_scraper.py
```

### 3. 執行進階 API 爬蟲（取得 JSON 格式的資料）

```bash
python nba_advanced_scraper.py
```

### 4. 分析爬取的資料

```bash
python nba_data_analyzer.py
```

### 5. 爬取並分析特定球員

```bash
python player_specific_scraper.py "球員名稱"
python player_specific_analyzer.py "球員ID"
```

### 6. 比較兩名球員

使用 ID 直接比較：
```bash
python player_comparison.py 球員1ID 球員2ID
```

使用名稱搜尋並比較：
```bash
python player_name_comparison.py "球員1名稱" "球員2名稱"
```

### 7. 輸出

- 基本 HTML 爬蟲的結果儲存在 `nba_data` 目錄中
- 進階 API 爬蟲的結果儲存在 `nba_data_json` 目錄中
- 球員資料儲存在 `nba_player_data` 目錄中
- 分析報告與圖表儲存在 `nba_analysis` 目錄中
- 球員分析結果儲存在 `nba_player_analysis` 目錄中
- 球員比較結果儲存在 `nba_player_comparison` 目錄中

## 將程式封裝成應用程式

### 使用 PyInstaller 封裝

PyInstaller 可以將 Python 程式封裝成獨立的應用程式，不需要使用者安裝 Python 或相依套件。

#### 1. 安裝 PyInstaller

```bash
pip install pyinstaller
```

#### 2. 封裝單一程式

```bash
# 封裝基本爬蟲程式
pyinstaller --onefile nba_scraper.py

# 封裝進階爬蟲程式
pyinstaller --onefile nba_advanced_scraper.py

# 封裝球員分析程式
pyinstaller --onefile player_specific_analyzer.py
```

#### 3. 建立整合式應用程式

如果您希望創建一個包含所有功能的應用程式，可以創建一個整合式介面：

```python
# 創建一個名為 nba_app.py 的檔案，整合所有功能
import sys
import os
import subprocess

def main_menu():
    print("===== NBA 資料爬蟲與分析工具 =====")
    print("1. 爬取 NBA 基本資料")
    print("2. 爬取 NBA 進階 API 資料")
    print("3. 爬取特定球員資料")
    print("4. 分析 NBA 整體資料")
    print("5. 分析特定球員資料")
    print("6. 比較兩名球員")
    print("0. 退出")
    
    choice = input("請選擇功能: ")
    
    if choice == "1":
        subprocess.run(["python", "nba_scraper.py"])
    elif choice == "2":
        subprocess.run(["python", "nba_advanced_scraper.py"])
    elif choice == "3":
        player_name = input("請輸入球員名稱: ")
        subprocess.run(["python", "player_specific_scraper.py", player_name])
    elif choice == "4":
        subprocess.run(["python", "nba_data_analyzer.py"])
    elif choice == "5":
        player_id = input("請輸入球員 ID: ")
        subprocess.run(["python", "player_specific_analyzer.py", player_id])
    elif choice == "6":
        compare_type = input("請選擇比較方式 (1: 使用名稱, 2: 使用 ID): ")
        if compare_type == "1":
            player1 = input("請輸入第一位球員名稱: ")
            player2 = input("請輸入第二位球員名稱: ")
            subprocess.run(["python", "player_name_comparison.py", player1, player2])
        else:
            player1 = input("請輸入第一位球員 ID: ")
            player2 = input("請輸入第二位球員 ID: ")
            subprocess.run(["python", "player_comparison.py", player1, player2])
    elif choice == "0":
        print("感謝使用！")
        sys.exit(0)
    else:
        print("無效的選擇，請重新輸入")
    
    # 返回主選單
    input("\n按 Enter 返回主選單...")
    main_menu()

if __name__ == "__main__":
    main_menu()
```

然後執行以下命令封裝整合式應用程式：

```bash
pyinstaller --onefile --name NBA數據分析工具 nba_app.py
```

完成後，封裝好的應用程式將位於 `dist` 目錄中。

## 分析功能

分析工具提供以下功能：

1. **競爭分析**：分析球隊排名、勝率和大派別差異
2. **球員分析**：分析球員分佈、國家統計和各隊人數
3. **選秀歷史分析**：分析歷年選秀趨勢和主要大學貢獻
4. **球員詳細分析**：包括生涯統計、每季表現趨勢和數據雷達圖
5. **球員比較**：直觀比較兩名球員的生涯數據和表現趨勢

## 注意事項

- 請尊重 NBA 網站的 robots.txt 規則
- 爬蟲程式中已設置適當的延遲，避免頻繁請求
- API 路徑可能會隨著 NBA 網站更新而變更，如果遇到問題，請檢查最新的 API 路徑
- 本專案僅作為學習和研究之用 