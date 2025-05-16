import requests
import time
import json
import os
import sys
from bs4 import BeautifulSoup

# 創建目錄來儲存爬取的資料
if not os.path.exists('nba_player_data'):
    os.makedirs('nba_player_data')

# 基本URL
base_url = 'https://www.nba.com'
api_base_url = 'https://stats.nba.com/stats'

# 用於發送請求的標頭
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'Referer': 'https://www.nba.com/',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'
}

# 函數：搜尋球員
def search_player(player_name):
    # 使用 NBA 的搜尋 API 或直接從球員列表中搜尋
    try:
        print(f'搜尋球員: {player_name}')
        player_endpoint = f'commonallplayers?LeagueID=00&Season=2024-25&IsOnlyCurrentSeason=1'
        response = requests.get(f'{api_base_url}/{player_endpoint}', headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if 'resultSets' in data and len(data['resultSets']) > 0:
                players_data = data['resultSets'][0]
                headers_list = players_data['headers']
                player_rows = players_data['rowSet']
                
                # 搜尋與所提供名稱相符的球員
                matching_players = []
                for player in player_rows:
                    # 建立球員資料字典
                    player_dict = {headers_list[i]: player[i] for i in range(len(headers_list))}
                    # 檢查球員名稱是否包含搜尋詞
                    if player_name.lower() in player_dict['DISPLAY_FIRST_LAST'].lower():
                        matching_players.append(player_dict)
                
                if matching_players:
                    print(f'找到 {len(matching_players)} 位符合的球員:')
                    for i, player in enumerate(matching_players):
                        print(f"{i+1}. {player['DISPLAY_FIRST_LAST']} (ID: {player['PERSON_ID']})")
                    return matching_players
                else:
                    print(f'找不到球員: {player_name}')
                    return []
            else:
                print('無法解析球員資料')
                return []
        else:
            print(f'搜尋失敗，狀態碼: {response.status_code}')
            return []
    except Exception as e:
        print(f'搜尋球員時發生錯誤: {e}')
        return []

# 函數：爬取球員基本資料
def fetch_player_profile(player_id):
    try:
        profile_url = f'{base_url}/player/{player_id}/profile'
        print(f'爬取球員個人資料頁面: {profile_url}')
        
        response = requests.get(profile_url, headers=headers)
        if response.status_code == 200:
            # 使用 BeautifulSoup 解析 HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 儲存原始 HTML (以便之後分析)
            with open(f'nba_player_data/player_{player_id}_profile.html', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            
            # 解析球員資料 (這部分可能需要根據網頁結構調整)
            player_info = {}
            
            # 嘗試獲取基本資訊
            try:
                player_info['name'] = soup.select_one('h1.PlayerSummary_playerNameText__K7ZXO').text.strip()
            except:
                player_info['name'] = 'N/A'
            
            # 嘗試獲取位置、球隊等其他基本資訊
            try:
                info_sections = soup.select('p.PlayerSummary_playerInfoText__JrK0r')
                for section in info_sections:
                    info_text = section.text.strip()
                    if '|' in info_text:
                        info_parts = info_text.split('|')
                        for part in info_parts:
                            if ':' in part:
                                key, value = part.split(':', 1)
                                player_info[key.strip().lower()] = value.strip()
            except Exception as e:
                print(f'獲取基本信息時出錯: {e}')
            
            # 儲存解析後的球員資訊
            with open(f'nba_player_data/player_{player_id}_info.json', 'w', encoding='utf-8') as f:
                json.dump(player_info, f, ensure_ascii=False, indent=4)
                
            print(f'成功儲存球員 {player_id} 的個人資料')
            return player_info
        else:
            print(f'獲取球員資料失敗，狀態碼: {response.status_code}')
            return None
    except Exception as e:
        print(f'爬取球員資料時發生錯誤: {e}')
        return None

# 函數：爬取球員統計數據
def fetch_player_stats(player_id):
    try:
        # 使用官方 API 獲取球員統計數據
        endpoint = f'playercareerstats?PlayerID={player_id}&PerMode=PerGame'
        print(f'獲取球員統計數據: {endpoint}')
        
        response = requests.get(f'{api_base_url}/{endpoint}', headers=headers)
        if response.status_code == 200:
            data = response.json()
            
            if 'resultSets' in data:
                # 儲存原始數據
                with open(f'nba_player_data/player_{player_id}_stats_raw.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                
                # 轉換為更易讀的格式
                stats = {}
                
                for result_set in data['resultSets']:
                    set_name = result_set['name']
                    headers_list = result_set['headers']
                    rows = result_set['rowSet']
                    
                    stats[set_name] = []
                    for row in rows:
                        stats[set_name].append({headers_list[i]: row[i] for i in range(len(headers_list))})
                
                # 儲存處理後的統計數據
                with open(f'nba_player_data/player_{player_id}_stats.json', 'w', encoding='utf-8') as f:
                    json.dump(stats, f, ensure_ascii=False, indent=4)
                
                print(f'成功儲存球員 {player_id} 的統計數據')
                return stats
            else:
                print('無法解析統計數據回應')
                return None
        else:
            print(f'獲取統計數據失敗，狀態碼: {response.status_code}')
            return None
    except Exception as e:
        print(f'爬取統計數據時發生錯誤: {e}')
        return None

# 主函數
def main():
    if len(sys.argv) > 1:
        # 從命令行參數獲取球員名稱
        player_name = ' '.join(sys.argv[1:]) if '--search-only' not in sys.argv else ' '.join([arg for arg in sys.argv[1:] if arg != '--search-only'])
        
        # 檢查是否為只搜尋模式
        search_only_mode = '--search-only' in sys.argv
    else:
        # 否則，提示用戶輸入
        player_name = input('請輸入要搜尋的球員名稱: ')
        search_only_mode = False
    
    if not player_name:
        print('錯誤：未提供球員名稱')
        return
    
    # 搜尋球員
    matching_players = search_player(player_name)
    
    # 如果是只搜尋模式，則在此處返回
    if search_only_mode:
        return
    
    if matching_players:
        if len(matching_players) > 1:
            # 如果找到多個匹配，讓用戶選擇
            try:
                choice = int(input('請輸入要查詢的球員編號: '))
                if choice < 1 or choice > len(matching_players):
                    print('無效的選擇')
                    return
                selected_player = matching_players[choice-1]
            except ValueError:
                print('無效的輸入，必須輸入數字')
                return
        else:
            # 只有一個匹配結果
            selected_player = matching_players[0]
        
        player_id = selected_player['PERSON_ID']
        print(f"\n開始爬取 {selected_player['DISPLAY_FIRST_LAST']} (ID: {player_id}) 的資料...")
        
        # 爬取球員基本資料
        player_info = fetch_player_profile(player_id)
        
        # 爬取球員統計數據
        player_stats = fetch_player_stats(player_id)
        
        print(f"\n所有 {selected_player['DISPLAY_FIRST_LAST']} 的資料爬取完成！\n")
        print(f"資料已儲存到 nba_player_data 目錄:")
        print(f"1. 個人資料頁: player_{player_id}_profile.html")
        print(f"2. 個人基本資訊: player_{player_id}_info.json")
        print(f"3. 統計數據: player_{player_id}_stats.json")

if __name__ == '__main__':
    main() 