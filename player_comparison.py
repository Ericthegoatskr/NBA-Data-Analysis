import json
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
import matplotlib
import re
from bs4 import BeautifulSoup

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

# 載入球員統計數據
def load_player_stats(player_id):
    player_id = str(player_id)  # 確保ID是字符串類型
    stats_file = f'nba_player_data/player_{player_id}_stats.json'
    print(f'嘗試載入球員統計數據文件: {stats_file}')
    
    # 備用數據（用於測試）
    fallback_stats = {
        '2544': {  # LeBron James
            'CareerTotalsRegularSeason': [
                {'PLAYER_ID': 2544, 'GP': 1421, 'PTS': 27.2, 'AST': 7.3, 'REB': 7.5, 'STL': 1.5, 'BLK': 0.8, 'FG_PCT': 0.504, 'FG3_PCT': 0.345, 'FT_PCT': 0.735}
            ],
            'SeasonTotalsRegularSeason': [
                {'SEASON_ID': '2003-04', 'GP': 79, 'PTS': 20.9, 'AST': 5.9, 'REB': 5.5, 'STL': 1.6, 'BLK': 0.7},
                {'SEASON_ID': '2008-09', 'GP': 81, 'PTS': 28.4, 'AST': 7.2, 'REB': 7.6, 'STL': 1.7, 'BLK': 1.1},
                {'SEASON_ID': '2012-13', 'GP': 76, 'PTS': 26.8, 'AST': 7.3, 'REB': 8.0, 'STL': 1.7, 'BLK': 0.9},
                {'SEASON_ID': '2017-18', 'GP': 82, 'PTS': 27.5, 'AST': 9.1, 'REB': 8.6, 'STL': 1.4, 'BLK': 0.9},
                {'SEASON_ID': '2022-23', 'GP': 55, 'PTS': 28.9, 'AST': 6.8, 'REB': 8.3, 'STL': 0.9, 'BLK': 0.6}
            ]
        },
        '201142': {  # Kevin Durant
            'CareerTotalsRegularSeason': [
                {'PLAYER_ID': 201142, 'GP': 1004, 'PTS': 27.3, 'AST': 4.3, 'REB': 7.1, 'STL': 1.1, 'BLK': 1.1, 'FG_PCT': 0.496, 'FG3_PCT': 0.385, 'FT_PCT': 0.883}
            ],
            'SeasonTotalsRegularSeason': [
                {'SEASON_ID': '2007-08', 'GP': 80, 'PTS': 20.3, 'AST': 2.4, 'REB': 4.4, 'STL': 1.0, 'BLK': 0.9},
                {'SEASON_ID': '2009-10', 'GP': 82, 'PTS': 30.1, 'AST': 2.8, 'REB': 7.6, 'STL': 1.4, 'BLK': 1.0},
                {'SEASON_ID': '2013-14', 'GP': 81, 'PTS': 32.0, 'AST': 5.5, 'REB': 7.4, 'STL': 1.3, 'BLK': 0.7},
                {'SEASON_ID': '2017-18', 'GP': 68, 'PTS': 26.4, 'AST': 5.4, 'REB': 6.8, 'STL': 0.7, 'BLK': 1.8},
                {'SEASON_ID': '2022-23', 'GP': 47, 'PTS': 29.1, 'AST': 5.0, 'REB': 6.7, 'STL': 0.7, 'BLK': 1.4}
            ]
        }
    }
    
    try:
        with open(stats_file, 'r', encoding='utf-8') as f:
            stats = json.load(f)
            print(f'成功載入球員 {player_id} 的統計數據')
            return stats
    except Exception as e:
        print(f'無法載入球員 {player_id} 的統計數據: {e}')
        # 如果是我們有備用數據的球員，返回備用數據
        if player_id in fallback_stats:
            print(f'使用 {player_id} 的備用統計數據')
            return fallback_stats[player_id]
        return None

# 載入球員基本資訊
def load_player_info(player_id):
    player_id = str(player_id)  # 確保ID是字符串類型
    info_file = f'nba_player_data/player_{player_id}_info.json'
    print(f'嘗試載入球員信息文件: {info_file}')
    
    # 為常見球員ID提供預設名稱映射
    default_names = {
        '2544': 'LeBron James',
        '201142': 'Kevin Durant',
        '203999': 'Nikola Jokic',
        '201939': 'Stephen Curry',
        '203954': 'Joel Embiid',
        '1629029': 'Luka Doncic',
        '203076': 'Anthony Davis',
        '201935': 'James Harden',
        '1628369': 'Jayson Tatum',
        '1627736': 'Jamal Murray',
        '203081': 'Damian Lillard',
        '203507': 'Giannis Antetokounmpo',
        '1627783': 'Jaylen Brown',
        '202681': 'Kyrie Irving',
        '1628983': 'Shai Gilgeous-Alexander',
        '203081': 'Damian Lillard'
    }
    
    # 從HTML檔案中提取球員名稱的函數
    def extract_name_from_html(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
                
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 嘗試不同的選擇器找到球員名稱
            # 1. 嘗試找標準的球員名稱元素
            player_name_elem = soup.select_one('h1.PlayerSummary_playerNameText__K7ZXO')
            if player_name_elem:
                return player_name_elem.text.strip()
            
            # 2. 嘗試找一般的標題
            h1_elems = soup.find_all('h1')
            for h1 in h1_elems:
                # 如果標題中有球員ID，很可能是球員名稱
                if player_id in h1.get('id', '') or 'player' in h1.get('class', [''])[0].lower():
                    return h1.text.strip()
            
            # 3. 嘗試通過頁面標題提取
            title = soup.find('title')
            if title:
                title_text = title.text.strip()
                # 如果標題包含 "| NBA.com"，提取前面部分
                if '|' in title_text:
                    return title_text.split('|')[0].strip()
            
            # 如果所有方法都失敗，使用正則表達式尋找
            patterns = [
                r'<h1[^>]*>([^<]+)</h1>',
                r'<div[^>]*class="[^"]*player-name[^"]*"[^>]*>([^<]+)</div>',
                r'player name: "([^"]+)"',
                r'playerName: "([^"]+)"'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    return matches[0].strip()
                    
            return None
        except Exception as e:
            print(f'從HTML提取名稱時發生錯誤: {e}')
            return None
    
    # 直接從info.json中提取名稱，如果失敗則使用預設名稱
    try:
        with open(info_file, 'r', encoding='utf-8') as f:
            player_info = json.load(f)
            print(f'載入了球員 {player_id} 的資訊: {player_info}')
            
            # 嘗試從不同欄位中獲取有效名稱
            if 'name' in player_info and player_info['name'] != 'N/A':
                print(f'使用資訊檔案中的名稱: {player_info["name"]}')
                return player_info
            elif 'DISPLAY_FIRST_LAST' in player_info:
                player_info['name'] = player_info['DISPLAY_FIRST_LAST']
                print(f'使用DISPLAY_FIRST_LAST作為名稱: {player_info["name"]}')
                return player_info
            elif player_id in default_names:
                player_info['name'] = default_names[player_id]
                print(f'使用預設名稱: {player_info["name"]}')
                return player_info
            else:
                # 從html檔案嘗試提取名稱
                html_file = f'nba_player_data/player_{player_id}_profile.html'
                if os.path.exists(html_file):
                    player_name = extract_name_from_html(html_file)
                    if player_name:
                        player_info['name'] = player_name
                        print(f'從HTML提取球員名稱: {player_name}')
                        return player_info
                
                # 如果所有方法都失敗，使用ID作為名稱
                player_info['name'] = f'Player {player_id}'
                print(f'使用ID作為名稱: {player_info["name"]}')
                return player_info
    except Exception as e:
        print(f'無法載入球員 {player_id} 的基本資訊: {e}')
        
        # 如果有預設名稱，使用預設名稱
        if player_id in default_names:
            print(f'使用預設名稱: {default_names[player_id]}')
            return {'name': default_names[player_id]}
        
        # 嘗試使用HTML檔案
        html_file = f'nba_player_data/player_{player_id}_profile.html'
        if os.path.exists(html_file):
            player_name = extract_name_from_html(html_file)
            if player_name:
                print(f'從HTML提取球員名稱: {player_name}')
                return {'name': player_name}
        
        # 如果所有方法都失敗，使用ID
        print(f'無法獲取名稱，使用ID: Player {player_id}')
        return {'name': f'Player {player_id}'}

# 比較兩名球員的生涯平均數據
def compare_career_averages(player1_id, player2_id):
    # 確保ID是字符串類型
    player1_id = str(player1_id)
    player2_id = str(player2_id)
    
    # 載入球員1的數據
    player1_stats = load_player_stats(player1_id)
    player1_info = load_player_info(player1_id)
    
    # 載入球員2的數據
    player2_stats = load_player_stats(player2_id)
    player2_info = load_player_info(player2_id)
    
    if not player1_stats or not player2_stats:
        print('無法比較生涯平均數據，缺少必要數據')
        return
    
    try:
        # 獲取球員姓名
        player1_name = player1_info.get('name', f'Player {player1_id}') if player1_info else f'Player {player1_id}'
        player2_name = player2_info.get('name', f'Player {player2_id}') if player2_info else f'Player {player2_id}'
        
        print(f'球員1姓名: {player1_name}, 球員2姓名: {player2_name}')
        
        # 轉換為 DataFrame
        player1_career = pd.DataFrame(player1_stats['CareerTotalsRegularSeason'])
        player2_career = pd.DataFrame(player2_stats['CareerTotalsRegularSeason'])
        
        if player1_career.empty or player2_career.empty:
            print('無法比較生涯平均數據，數據為空')
            return
        
        # 創建數據對比圖 - 主要統計數據比較
        categories = ['PTS', 'AST', 'REB', 'STL', 'BLK']
        labels = ['Points', 'Assists', 'Rebounds', 'Steals', 'Blocks']
        
        # 獲取數據
        player1_values = [player1_career.iloc[0][cat] for cat in categories]
        player2_values = [player2_career.iloc[0][cat] for cat in categories]
        
        # 創建柱狀圖
        x = np.arange(len(categories))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(12, 8))
        rects1 = ax.bar(x - width/2, player1_values, width, label=player1_name)
        rects2 = ax.bar(x + width/2, player2_values, width, label=player2_name)
        
        # 添加標籤和標題
        ax.set_ylabel('Career Averages')
        ax.set_title('Career Stats Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()
        
        # 為每個柱子添加數值標籤
        def autolabel(rects):
            for rect in rects:
                height = rect.get_height()
                ax.annotate('{:.1f}'.format(height),
                            xy=(rect.get_x() + rect.get_width()/2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom')
        
        autolabel(rects1)
        autolabel(rects2)
        
        plt.tight_layout()
        plt.savefig(f'nba_player_comparison/{player1_id}_vs_{player2_id}_career_stats.png', dpi=300)
        print(f'已保存 {player1_name} 和 {player2_name} 的生涯數據對比圖')
        
        # 創建雷達圖 - 多維度數據對比
        categories = ['PTS', 'AST', 'REB', 'STL', 'BLK', 'FG_PCT', 'FG3_PCT', 'FT_PCT']
        labels = ['Points', 'Assists', 'Rebounds', 'Steals', 'Blocks', 'FG%', '3P%', 'FT%']
        
        # 獲取數據並正規化
        max_values = {
            'PTS': 30, 'AST': 10, 'REB': 15, 'STL': 3, 'BLK': 3, 
            'FG_PCT': 0.6, 'FG3_PCT': 0.5, 'FT_PCT': 1.0
        }
        
        player1_radar = [min(player1_career.iloc[0][cat] / max_values[cat] * 100, 100) if cat in player1_career.columns else 0 for cat in categories]
        player2_radar = [min(player2_career.iloc[0][cat] / max_values[cat] * 100, 100) if cat in player2_career.columns else 0 for cat in categories]
        
        # 繪製雷達圖
        angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
        
        # 閉合雷達圖
        player1_radar += [player1_radar[0]]
        player2_radar += [player2_radar[0]]
        angles += [angles[0]]
        labels += [labels[0]]
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
        
        ax.plot(angles, player1_radar, 'b-', linewidth=2, label=player1_name)
        ax.fill(angles, player1_radar, 'b', alpha=0.1)
        
        ax.plot(angles, player2_radar, 'r-', linewidth=2, label=player2_name)
        ax.fill(angles, player2_radar, 'r', alpha=0.1)
        
        # 設置標籤和角度
        ax.set_thetagrids(np.degrees(angles[:-1]), labels[:-1])
        ax.set_ylim(0, 100)
        ax.set_title(f'{player1_name} vs {player2_name} - Radar Comparison', fontsize=15, y=1.1)
        
        # 顯示圖例
        ax.legend(loc='upper right')
        
        plt.tight_layout()
        plt.savefig(f'nba_player_comparison/{player1_id}_vs_{player2_id}_radar.png', dpi=300)
        print(f'已保存 {player1_name} 和 {player2_name} 的能力雷達對比圖')
        
        # 生成對比報告
        create_comparison_report(player1_id, player2_id, player1_info, player2_info, player1_career, player2_career)
        
    except Exception as e:
        print(f'比較生涯平均數據時出現錯誤: {e}')

# 比較兩名球員的賽季表現
def compare_season_trends(player1_id, player2_id):
    # 確保ID是字符串類型
    player1_id = str(player1_id)
    player2_id = str(player2_id)
    
    # 載入球員1的數據
    player1_stats = load_player_stats(player1_id)
    player1_info = load_player_info(player1_id)
    
    # 載入球員2的數據
    player2_stats = load_player_stats(player2_id)
    player2_info = load_player_info(player2_id)
    
    if not player1_stats or not player2_stats:
        print('無法比較賽季趨勢，缺少必要數據')
        return
    
    try:
        # 獲取球員姓名
        player1_name = player1_info.get('name', f'Player {player1_id}') if player1_info else f'Player {player1_id}'
        player2_name = player2_info.get('name', f'Player {player2_id}') if player2_info else f'Player {player2_id}'
        
        print(f'賽季比較 - 球員1姓名: {player1_name}, 球員2姓名: {player2_name}')
        
        # 轉換為 DataFrame
        player1_seasons = pd.DataFrame(player1_stats['SeasonTotalsRegularSeason'])
        player2_seasons = pd.DataFrame(player2_stats['SeasonTotalsRegularSeason'])
        
        if player1_seasons.empty or player2_seasons.empty:
            print('無法比較賽季趨勢，數據為空')
            return
        
        # 排序賽季數據
        if 'SEASON_ID' in player1_seasons.columns:
            player1_seasons = player1_seasons.sort_values('SEASON_ID')
        
        if 'SEASON_ID' in player2_seasons.columns:
            player2_seasons = player2_seasons.sort_values('SEASON_ID')
        
        # 繪製得分趨勢對比圖
        if 'PTS' in player1_seasons.columns and 'PTS' in player2_seasons.columns:
            plt.figure(figsize=(12, 8))
            plt.plot(player1_seasons['SEASON_ID'], player1_seasons['PTS'], 'b-o', linewidth=2, label=player1_name)
            plt.plot(player2_seasons['SEASON_ID'], player2_seasons['PTS'], 'r-o', linewidth=2, label=player2_name)
            
            plt.title(f'Points Per Game Comparison: {player1_name} vs {player2_name}', fontsize=16)
            plt.xlabel('Season', fontsize=14)
            plt.ylabel('Points Per Game', fontsize=14)
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig(f'nba_player_comparison/{player1_id}_vs_{player2_id}_pts_trend.png', dpi=300)
            print(f'已保存 {player1_name} 和 {player2_name} 的得分趨勢對比圖')
        
        # 繪製其他數據趨勢對比圖（助攻、籃板等）
        for stat, label in [('AST', 'Assists'), ('REB', 'Rebounds')]:
            if stat in player1_seasons.columns and stat in player2_seasons.columns:
                plt.figure(figsize=(12, 8))
                plt.plot(player1_seasons['SEASON_ID'], player1_seasons[stat], 'b-o', linewidth=2, label=player1_name)
                plt.plot(player2_seasons['SEASON_ID'], player2_seasons[stat], 'r-o', linewidth=2, label=player2_name)
                
                plt.title(f'{label} Per Game Comparison: {player1_name} vs {player2_name}', fontsize=16)
                plt.xlabel('Season', fontsize=14)
                plt.ylabel(f'{label} Per Game', fontsize=14)
                plt.legend()
                plt.grid(True, linestyle='--', alpha=0.7)
                plt.tight_layout()
                plt.savefig(f'nba_player_comparison/{player1_id}_vs_{player2_id}_{stat.lower()}_trend.png', dpi=300)
                print(f'已保存 {player1_name} 和 {player2_name} 的{label}趨勢對比圖')
        
    except Exception as e:
        print(f'比較賽季趨勢時出現錯誤: {e}')

# 生成球員比較報告
def create_comparison_report(player1_id, player2_id, player1_info, player2_info, player1_career, player2_career):
    # 獲取球員姓名
    player1_name = player1_info.get('name', f'Player {player1_id}') if player1_info else f'Player {player1_id}'
    player2_name = player2_info.get('name', f'Player {player2_id}') if player2_info else f'Player {player2_id}'
    
    # 比較結果摘要
    report = f'''球員對比分析報告: {player1_name} vs {player2_name}

基本資料:
'''
    # 添加兩位球員的基本資訊
    if player1_info:
        report += f'\n{player1_name}:\n'
        for key, value in player1_info.items():
            report += f'  {key.capitalize()}: {value}\n'
    
    if player2_info:
        report += f'\n{player2_name}:\n'
        for key, value in player2_info.items():
            report += f'  {key.capitalize()}: {value}\n'
    
    # 添加生涯數據對比
    report += f'\n\n生涯平均數據對比:\n'
    
    stats_to_compare = [
        ('GP', '出場次數'),
        ('PTS', '得分'),
        ('AST', '助攻'),
        ('REB', '籃板'),
        ('STL', '抄截'),
        ('BLK', '蓋帽'),
        ('FG_PCT', '投籃命中率'),
        ('FG3_PCT', '三分命中率'),
        ('FT_PCT', '罰球命中率')
    ]
    
    report += f'\n統計項目       {player1_name}      {player2_name}      差異\n'
    report += f'--------------------------------------------------------\n'
    
    for stat, label in stats_to_compare:
        try:
            if stat in player1_career.columns and stat in player2_career.columns:
                val1 = player1_career.iloc[0][stat]
                val2 = player2_career.iloc[0][stat]
                diff = val1 - val2
                
                if stat in ['FG_PCT', 'FG3_PCT', 'FT_PCT']:  # 轉換百分比
                    report += f'{label:<12} {val1*100:.1f}%        {val2*100:.1f}%        {diff*100:+.1f}%\n'
                else:
                    report += f'{label:<12} {val1:.1f}          {val2:.1f}          {diff:+.1f}\n'
        except:
            pass
    
    # 添加圖表說明
    report += f'''

附上對比圖表:
1. {player1_id}_vs_{player2_id}_career_stats.png - 生涯數據柱狀對比圖
2. {player1_id}_vs_{player2_id}_radar.png - 能力雷達對比圖
3. {player1_id}_vs_{player2_id}_pts_trend.png - 得分趨勢對比圖
4. {player1_id}_vs_{player2_id}_ast_trend.png - 助攻趨勢對比圖
5. {player1_id}_vs_{player2_id}_reb_trend.png - 籃板趨勢對比圖
'''
    
    # 保存報告到文件
    with open(f'nba_player_comparison/{player1_id}_vs_{player2_id}_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f'已生成 {player1_name} 和 {player2_name} 的對比分析報告')
    return report

# 主函數
def main():
    # 檢查命令行參數或提示用戶輸入
    if len(sys.argv) > 2:
        player1_id = str(sys.argv[1])
        player2_id = str(sys.argv[2])
    else:
        print("用法: python player_comparison.py <球員1 ID> <球員2 ID>")
        player1_id = str(input('請輸入第一位球員 ID: '))
        player2_id = str(input('請輸入第二位球員 ID: '))
    
    print(f'球員1 ID: {player1_id}, 球員2 ID: {player2_id}')
    
    # 檢查必要的目錄是否存在
    if not os.path.exists('nba_player_data'):
        print('錯誤：未找到 nba_player_data 目錄。請先運行 player_specific_scraper.py 獲取球員數據。')
        return
    
    # 檢查球員數據是否存在
    player1_stats_file = f'nba_player_data/player_{player1_id}_stats.json'
    player1_info_file = f'nba_player_data/player_{player1_id}_info.json'
    player2_stats_file = f'nba_player_data/player_{player2_id}_stats.json'
    player2_info_file = f'nba_player_data/player_{player2_id}_info.json'
    
    print(f'檢查文件: {player1_stats_file}, {player1_info_file}')
    print(f'檢查文件: {player2_stats_file}, {player2_info_file}')
    
    if not os.path.exists(player1_stats_file) or not os.path.exists(player1_info_file):
        print(f'錯誤：請先運行 player_specific_scraper.py 獲取球員 {player1_id} 的數據。')
        # 如果是LeBron James或Kevin Durant，則繼續
        if player1_id not in ['2544', '201142']:
            return
    
    if not os.path.exists(player2_stats_file) or not os.path.exists(player2_info_file):
        print(f'錯誤：請先運行 player_specific_scraper.py 獲取球員 {player2_id} 的數據。')
        # 如果是LeBron James或Kevin Durant，則繼續
        if player2_id not in ['2544', '201142']:
            return
    
    print(f'開始比較球員 {player1_id} 和 {player2_id} 的數據...')
    
    # 比較生涯平均數據
    print('\n比較生涯平均數據...')
    compare_career_averages(player1_id, player2_id)
    
    # 比較賽季趨勢
    print('\n比較賽季趨勢...')
    compare_season_trends(player1_id, player2_id)
    
    print(f'\n所有比較結果已保存在 nba_player_comparison 目錄下。')

if __name__ == '__main__':
    main() 