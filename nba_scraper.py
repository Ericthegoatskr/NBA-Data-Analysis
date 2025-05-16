import requests
import time
from bs4 import BeautifulSoup
import json
import os

# 創建目錄來儲存爬取的資料
if not os.path.exists('nba_data'):
    os.makedirs('nba_data')

# 根據robots.txt允許的路徑
allowed_paths = [
    '/standings',              # 球隊排名
    '/schedule',               # 賽程表
    '/stats/help/glossary',    # 數據術語表
    '/stats/draft/history',    # 選秀歷史
    '/stats/help/statminimums',# 數據最低標準
    '/stats/history',          # 歷史數據
    '/players',                # 球員名單
]

# 球隊頁面需要單獨處理
teams = ['celtics','warriors','lakers']

# 基本URL
base_url = 'https://www.nba.com'

# 用於發送請求的標頭
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
}

# 函數：爬取一個頁面並保存
def scrape_page(url, filename):
    try:
        print(f'正在爬取: {url}')
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            with open(f'nba_data/{filename}.html', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            print(f'成功保存: {filename}.html')
            return soup
        else:
            print(f'請求失敗，狀態碼: {response.status_code}')
            return None
    except Exception as e:
        print(f'爬取錯誤: {e}')
        return None

# 函數：爬取球員資料
def scrape_players():
    soup = scrape_page(f'{base_url}/players', 'players_list')
    if soup:
        # 尋找球員連結
        player_links = []
        # 注意：以下選擇器可能需要根據實際網頁結構調整
        for link in soup.select('a[href*="/player/"]'):
            href = link.get('href')
            if href and 'profile' in href:
                player_links.append(href)
        
        # 保存找到的球員鏈接
        with open('nba_data/player_links.json', 'w', encoding='utf-8') as f:
            json.dump(player_links, f, ensure_ascii=False, indent=4)
        
        # 爬取前5個球員資料（作為示例，避免爬取過多）
        for i, player_link in enumerate(player_links[:5]):
            player_url = base_url + player_link if not player_link.startswith('http') else player_link
            player_id = player_link.split('/')[-1]
            scrape_page(player_url, f'player_{player_id}')
            time.sleep(1)  # 避免請求過於頻繁

# 函數：爬取球隊資料
def scrape_teams():
    for team in teams:
        team_url = f'{base_url}/team/{team}'
        scrape_page(team_url, f'team_{team}')
        time.sleep(1)  # 避免請求過於頻繁

# 開始爬取
def main():
    # 爬取允許的頁面
    for path in allowed_paths:
        page_name = path.replace('/', '_').strip('_')
        scrape_page(base_url + path, page_name)
        time.sleep(1)  # 避免請求過於頻繁
    
    # 爬取球員資料
    print('\n開始爬取球員資料...')
    scrape_players()
    
    # 爬取球隊資料
    print('\n開始爬取球隊資料...')
    scrape_teams()

if __name__ == '__main__':
    main()
    print('所有資料爬取完成！') 