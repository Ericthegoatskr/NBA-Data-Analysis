import json
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
import matplotlib
import re
from bs4 import BeautifulSoup
import subprocess

# 設置通用字體
try:
    matplotlib.rcParams['font.family'] = ['Arial', 'sans-serif']
    matplotlib.rcParams['axes.unicode_minus'] = False
    print('已設置通用字體支援')
except:
    print('警告：設置字體失敗，圖表中的文字可能無法正確顯示')

# 確保存儲分析結果的目錄存在
if not os.path.exists('nba_player_comparison'):
    os.makedirs('nba_player_comparison')

# 使用球員名稱搜尋球員ID
def search_player(player_name):
    try:
        print(f'搜尋球員: {player_name}')
        # 使用player_specific_scraper.py的搜尋功能
        result = subprocess.run(
            ['python', 'player_specific_scraper.py', player_name, '--search-only'],
            capture_output=True,
            text=True
        )
        
        output = result.stdout
        print(output)
        
        # 解析輸出以獲取球員ID
        player_ids = []
        for line in output.splitlines():
            # 查找格式如 "1. Player Name (ID: 12345)" 的行
            match = re.search(r'(\d+)\.\s+(.*?)\s+\(ID:\s+(\d+)\)', line)
            if match:
                index = match.group(1)
                name = match.group(2)
                player_id = match.group(3)
                player_ids.append((index, name, player_id))
        
        return player_ids
    except Exception as e:
        print(f'搜尋球員時發生錯誤: {e}')
        return []

# 修改player_specific_scraper.py以添加搜尋功能
def update_scraper_for_search():
    if not os.path.exists('player_specific_scraper.py'):
        print('找不到爬蟲程式 player_specific_scraper.py')
        return False
    
    with open('player_specific_scraper.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 確認是否需要修改
    if '--search-only' not in content:
        print('修改爬蟲程式以支援只搜尋模式...')
        
        # 修改main函數以支援--search-only參數
        main_func_pattern = r'def main\(\):(.*?)if __name__ == \'__main__\':'
        main_func_match = re.search(main_func_pattern, content, re.DOTALL)
        
        if main_func_match:
            old_main = main_func_match.group(1)
            new_main = '\n    # 檢查是否為只搜尋模式\n    if len(sys.argv) > 2 and sys.argv[2] == "--search-only":\n        matching_players = search_player(player_name)\n        return\n' + old_main
            
            content = content.replace(old_main, new_main)
            
            with open('player_specific_scraper.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print('已成功修改爬蟲程式')
            return True
    else:
        print('爬蟲程式已支援只搜尋模式')
        return True
    
    return False

# 主函數
def main():
    # 檢查並更新爬蟲程式
    if not update_scraper_for_search():
        print('無法修改爬蟲程式，請手動添加--search-only參數支援')
        print('繼續嘗試使用名稱比較...')
    
    # 檢查命令行參數或提示用戶輸入
    if len(sys.argv) > 2:
        player1_name = sys.argv[1]
        player2_name = sys.argv[2]
    else:
        print("用法: python player_name_comparison.py <球員1名稱> <球員2名稱>")
        player1_name = input('請輸入第一位球員名稱: ')
        player2_name = input('請輸入第二位球員名稱: ')
    
    print(f'球員1名稱: {player1_name}, 球員2名稱: {player2_name}')
    
    # 搜尋並獲取球員ID
    player1_results = search_player(player1_name)
    if not player1_results:
        print(f'找不到球員: {player1_name}')
        print('嘗試爬取數據...')
        # 嘗試爬取球員數據
        subprocess.run(['python', 'player_specific_scraper.py', player1_name])
        # 再次搜尋
        player1_results = search_player(player1_name)
        if not player1_results:
            print(f'無法爬取或找到球員: {player1_name}')
            return
    
    player2_results = search_player(player2_name)
    if not player2_results:
        print(f'找不到球員: {player2_name}')
        print('嘗試爬取數據...')
        # 嘗試爬取球員數據
        subprocess.run(['python', 'player_specific_scraper.py', player2_name])
        # 再次搜尋
        player2_results = search_player(player2_name)
        if not player2_results:
            print(f'無法爬取或找到球員: {player2_name}')
            return
    
    # 如果有多個結果，讓用戶選擇
    player1_id = None
    if len(player1_results) > 1:
        print(f'找到多個符合 "{player1_name}" 的球員:')
        for idx, name, player_id in player1_results:
            print(f"{idx}. {name} (ID: {player_id})")
        selection = input('請選擇第一位球員的編號: ')
        try:
            selected_idx = int(selection) - 1
            if 0 <= selected_idx < len(player1_results):
                _, selected_name, player1_id = player1_results[selected_idx]
                print(f'已選擇: {selected_name} (ID: {player1_id})')
            else:
                print('無效的選擇')
                return
        except ValueError:
            print('請輸入有效的數字')
            return
    else:
        _, selected_name, player1_id = player1_results[0]
        print(f'已選擇: {selected_name} (ID: {player1_id})')
    
    player2_id = None
    if len(player2_results) > 1:
        print(f'找到多個符合 "{player2_name}" 的球員:')
        for idx, name, player_id in player2_results:
            print(f"{idx}. {name} (ID: {player_id})")
        selection = input('請選擇第二位球員的編號: ')
        try:
            selected_idx = int(selection) - 1
            if 0 <= selected_idx < len(player2_results):
                _, selected_name, player2_id = player2_results[selected_idx]
                print(f'已選擇: {selected_name} (ID: {player2_id})')
            else:
                print('無效的選擇')
                return
        except ValueError:
            print('請輸入有效的數字')
            return
    else:
        _, selected_name, player2_id = player2_results[0]
        print(f'已選擇: {selected_name} (ID: {player2_id})')
    
    # 確保爬取了球員數據
    player1_stats_file = f'nba_player_data/player_{player1_id}_stats.json'
    player2_stats_file = f'nba_player_data/player_{player2_id}_stats.json'
    
    if not os.path.exists(player1_stats_file):
        print(f'爬取 {selected_name} 的數據...')
        subprocess.run(['python', 'player_specific_scraper.py', player1_name])
    
    if not os.path.exists(player2_stats_file):
        print(f'爬取 {selected_name} 的數據...')
        subprocess.run(['python', 'player_specific_scraper.py', player2_name])
    
    # 運行比較
    print(f'使用球員ID進行比較: {player1_id} vs {player2_id}')
    subprocess.run(['python', 'player_comparison.py', player1_id, player2_id])
    
    print('比較完成！結果已保存到 nba_player_comparison 目錄')

if __name__ == '__main__':
    main() 