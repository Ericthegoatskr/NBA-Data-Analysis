import json
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib

# 設置中文字體
try:
    # 嘗試設置為系統中可用的中文字體
    matplotlib.rcParams['font.family'] = ['Arial Unicode MS', 'Microsoft YaHei', 'SimHei', 'sans-serif']
    # 解決負號顯示問題
    matplotlib.rcParams['axes.unicode_minus'] = False
    print('已設置中文字體支援')
except:
    print('警告：無法設置中文字體，圖表中的中文可能無法正確顯示')

# 確保我們有儲存分析結果的目錄
if not os.path.exists('nba_analysis'):
    os.makedirs('nba_analysis')

# 導入數據函數
def load_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f'無法讀取檔案 {file_path}: {e}')
        return None

# 分析球隊排名
def analyze_standings():
    file_path = 'nba_data_json/standings.json'
    standings = load_data(file_path)
    
    if not standings:
        print('無法分析球隊排名資料')
        return
    
    # 轉換為 DataFrame
    df = pd.DataFrame(standings)
    
    # 選擇感興趣的欄位
    try:
        columns_of_interest = ['TEAM', 'WINS', 'LOSSES', 'WIN_PCT', 'CONFERENCE']
        selected_df = df[columns_of_interest]
        
        # 依照勝率排序
        sorted_df = selected_df.sort_values('WIN_PCT', ascending=False)
        
        # 儲存分析結果
        sorted_df.to_csv('nba_analysis/team_standings_analysis.csv', index=False)
        print('成功儲存球隊排名分析')
        
        # 創建視覺化：勝率最高的5支球隊
        plt.figure(figsize=(10, 6))
        top_teams = sorted_df.head(5)
        plt.bar(top_teams['TEAM'], top_teams['WIN_PCT'], color='blue')
        plt.title('勝率最高的5支球隊')
        plt.xlabel('球隊')
        plt.ylabel('勝率')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('nba_analysis/top_teams_win_pct.png', dpi=300)
        print('成功創建勝率最高的5支球隊圖表')
        
        # 按東西部分析
        if 'CONFERENCE' in df.columns:
            conference_wins = df.groupby('CONFERENCE')['WINS'].mean().reset_index()
            print('\n東西部競爭差異:')
            print(conference_wins)
    except Exception as e:
        print(f'分析球隊排名時發生錯誤: {e}')

# 分析球員數據
def analyze_players():
    file_path = 'nba_data_json/players.json'
    players = load_data(file_path)
    
    if not players:
        print('無法分析球員資料')
        return
    
    # 轉換為 DataFrame
    df = pd.DataFrame(players)
    
    try:
        # 按球隊分析球員數量
        if 'TEAM_ID' in df.columns and 'TEAM_NAME' in df.columns:
            team_counts = df.groupby('TEAM_NAME').size().reset_index(name='PLAYER_COUNT')
            team_counts_sorted = team_counts.sort_values('PLAYER_COUNT', ascending=False)
            
            # 儲存分析結果
            team_counts_sorted.to_csv('nba_analysis/team_player_counts.csv', index=False)
            print('成功儲存球隊球員數量分析')
            
            # 創建視覺化
            plt.figure(figsize=(12, 8))
            plt.bar(team_counts_sorted['TEAM_NAME'], team_counts_sorted['PLAYER_COUNT'], color='green')
            plt.title('每支球隊的球員數量')
            plt.xlabel('球隊')
            plt.ylabel('球員數量')
            plt.xticks(rotation=90)
            plt.tight_layout()
            plt.savefig('nba_analysis/team_player_counts.png', dpi=300)
            print('成功創建球隊球員數量圖表')
        
        # 分析國家分佈
        if 'COUNTRY' in df.columns:
            country_counts = df.groupby('COUNTRY').size().reset_index(name='PLAYER_COUNT')
            country_counts_sorted = country_counts.sort_values('PLAYER_COUNT', ascending=False)
            
            # 儲存分析結果
            country_counts_sorted.to_csv('nba_analysis/player_country_analysis.csv', index=False)
            print('成功儲存球員國家分佈分析')
            
            # 只顯示前10個國家
            top_countries = country_counts_sorted.head(10)
            plt.figure(figsize=(10, 6))
            plt.bar(top_countries['COUNTRY'], top_countries['PLAYER_COUNT'], color='orange')
            plt.title('球員數量最多的10個國家')
            plt.xlabel('國家')
            plt.ylabel('球員數量')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig('nba_analysis/player_country_distribution.png', dpi=300)
            print('成功創建球員國家分佈圖表')
    except Exception as e:
        print(f'分析球員數據時發生錯誤: {e}')

# 分析選秀歷史
def analyze_draft_history():
    file_path = 'nba_data_json/draft_history.json'
    draft_history = load_data(file_path)
    
    if not draft_history:
        print('無法分析選秀歷史資料')
        return
    
    # 轉換為 DataFrame
    df = pd.DataFrame(draft_history)
    
    try:
        # 分析各年選秀人數
        if 'SEASON' in df.columns:
            draft_counts = df.groupby('SEASON').size().reset_index(name='DRAFT_COUNT')
            draft_counts_sorted = draft_counts.sort_values('SEASON', ascending=True)
            
            # 儲存分析結果
            draft_counts_sorted.to_csv('nba_analysis/draft_counts_by_year.csv', index=False)
            print('成功儲存各年選秀人數分析')
            
            # 創建視覺化（顯示最近20年）
            recent_years = draft_counts_sorted.tail(20)
            plt.figure(figsize=(12, 6))
            plt.plot(recent_years['SEASON'], recent_years['DRAFT_COUNT'], marker='o', linestyle='-')
            plt.title('最近20年每年選秀人數')
            plt.xlabel('年度')
            plt.ylabel('選秀人數')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig('nba_analysis/draft_count_trend.png', dpi=300)
            print('成功創建選秀人數趨勢圖')
        
        # 分析各大學選秀人數
        if 'ORGANIZATION' in df.columns:
            college_counts = df.groupby('ORGANIZATION').size().reset_index(name='DRAFT_COUNT')
            college_counts_sorted = college_counts.sort_values('DRAFT_COUNT', ascending=False)
            
            # 只保留十大學校及簡化圖表（排除空值）
            top_colleges = college_counts_sorted[
                (college_counts_sorted['ORGANIZATION'].notna()) & 
                (college_counts_sorted['ORGANIZATION'] != '')
            ].head(10)
            
            # 儲存分析結果
            top_colleges.to_csv('nba_analysis/top_draft_colleges.csv', index=False)
            print('成功儲存選秀人數最多的十大學校分析')
            
            # 創建視覺化
            plt.figure(figsize=(15, 7))
            bars = plt.bar(top_colleges['ORGANIZATION'], top_colleges['DRAFT_COUNT'], color='purple')
            plt.title('選秀人數最多的十大學校', fontsize=16)
            plt.xlabel('學校/組織', fontsize=14)
            plt.ylabel('選秀人數', fontsize=14)
            plt.xticks(rotation=45, fontsize=12)
            plt.yticks(fontsize=12)
            
            # 在每個長條上顯示數值
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{int(height)}',
                        ha='center', va='bottom', fontsize=12)
            
            plt.tight_layout()
            plt.savefig('nba_analysis/top_draft_colleges.png', dpi=300)
            print('成功創建選秀學校分析圖')
    except Exception as e:
        print(f'分析選秀歷史時發生錯誤: {e}')

# 寫入分析報告
def write_summary_report():
    report = '''分析報告： NBA 爬取數據的洞察

本報告結合所有分析結果，提供對 NBA 數據的全面洞察。

1. 競爭分析（排名資料）
   - 已分析每支球隊的勝負與勝率
   - 東西部競爭差異比較
   - 堅持追蹤排名頂端的球隊

2. 球員分析
   - 已分析每支球隊的球員數量
   - 已剖析國家分佈，顯示 NBA 的國際化程度

3. 選秀分析
   - 已分析歷年選秀人數趨勢
   - 已辨識出提供最多 NBA 選手的大學
   - 已追蹤選秀模式的歷史變化

結論：NBA 的數據顯示了它全球性的影響力和高度競爭的特性。這些分析提供了對聯盟發展趨勢的洞察，並可能有助於預測未來的發展方向。
'''
    
    with open('nba_analysis/summary_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    print('成功創建分析報告')

# 主函數
def main():
    print('開始分析 NBA 數據...')
    
    # 確保資料目錄存在
    if not os.path.exists('nba_data_json'):
        print('錯誤：沒有找到數據目錄。請先執行爬蟲程式。')
        return
    
    # 分析競爭陣容
    print('\n分析球隊排名資料...')
    analyze_standings()
    
    # 分析球員數據
    print('\n分析球員資料...')
    analyze_players()
    
    # 分析選秀歷史
    print('\n分析選秀歷史...')
    analyze_draft_history()
    
    # 創建報告
    print('\n創建分析報告...')
    write_summary_report()
    
    print('\n所有分析完成！結果已儲存在 nba_analysis 目錄中。')

if __name__ == '__main__':
    main() 