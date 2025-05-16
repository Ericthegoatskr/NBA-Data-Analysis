import json
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
import matplotlib

# 設置中文字體
try:
    # 使用通用字體
    matplotlib.rcParams['font.family'] = ['Arial', 'sans-serif']
    # 解決保存圖像時負號'-'顯示為方塊的問題
    matplotlib.rcParams['axes.unicode_minus'] = False
    print('已設置通用字體支援')
except:
    print('警告：設置字體失敗，圖表中的中文可能無法正確顯示')

# 确保存储分析结果的目录存在
if not os.path.exists('nba_player_analysis'):
    os.makedirs('nba_player_analysis')

# 加载球员统计数据
def load_player_stats(player_id):
    stats_file = f'nba_player_data/player_{player_id}_stats.json'
    try:
        with open(stats_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f'无法加载球员统计数据: {e}')
        return None

# 加载球员信息
def load_player_info(player_id):
    info_file = f'nba_player_data/player_{player_id}_info.json'
    try:
        with open(info_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f'无法加载球员信息: {e}')
        return None

# 分析职业平均数据
def analyze_career_averages(stats):
    if not stats or 'CareerTotalsRegularSeason' not in stats:
        print('无法分析职业平均数据，缺少必要数据')
        return None
    
    try:
        # 转换为 DataFrame
        career_stats = pd.DataFrame(stats['CareerTotalsRegularSeason'])
        
        if career_stats.empty:
            print('无法分析职业平均数据，数据为空')
            return None
        
        return career_stats
    except Exception as e:
        print(f'分析职业平均数据时出现错误: {e}')
        return None

# 分析每年表现
def analyze_season_by_season(stats, player_info, player_id):
    if not stats or 'SeasonTotalsRegularSeason' not in stats:
        print('無法分析每年數據，缺少必要數據')
        return None
    
    try:
        # 轉換為 DataFrame
        season_stats = pd.DataFrame(stats['SeasonTotalsRegularSeason'])
        
        if season_stats.empty:
            print('無法分析每年數據，數據為空')
            return None
        
        # 確保所需的列存在
        required_columns = ['SEASON_ID', 'TEAM_ABBREVIATION', 'GP', 'PTS', 'AST', 'REB', 'STL', 'BLK']
        if not all(col in season_stats.columns for col in required_columns):
            missing_cols = [col for col in required_columns if col not in season_stats.columns]
            print(f'缺少必要的列: {missing_cols}')
            # 嘗試使用可用的列
            available_columns = [col for col in required_columns if col in season_stats.columns]
            if not available_columns:
                return None
            required_columns = available_columns
        
        # 按年份排序
        if 'SEASON_ID' in season_stats.columns:
            season_stats = season_stats.sort_values('SEASON_ID')
        
        # 獲取球員姓名
        player_name = player_info.get('name', 'Unknown Player') if player_info else 'Unknown Player'
        
        # 分析平均得分趨勢
        plt.figure(figsize=(12, 6))
        if 'PTS' in season_stats.columns and 'SEASON_ID' in season_stats.columns:
            plt.plot(season_stats['SEASON_ID'], season_stats['PTS'], 'b-o', linewidth=2)
            plt.title(f'{player_name} Points Per Game Trend', fontsize=16)
            plt.xlabel('Season', fontsize=14)
            plt.ylabel('Points Per Game', fontsize=14)
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig(f'nba_player_analysis/player_{player_id}_pts_trend.png', dpi=300)
            print(f'已保存球員平均得分趨勢圖')
        
        # 分析平均得分、助攻、籃板的對比
        if all(col in season_stats.columns for col in ['PTS', 'AST', 'REB', 'SEASON_ID']):
            plt.figure(figsize=(12, 6))
            plt.plot(season_stats['SEASON_ID'], season_stats['PTS'], 'b-o', label='Points')
            plt.plot(season_stats['SEASON_ID'], season_stats['AST'], 'r-o', label='Assists')
            plt.plot(season_stats['SEASON_ID'], season_stats['REB'], 'g-o', label='Rebounds')
            plt.title(f'{player_name} Stats Comparison', fontsize=16)
            plt.xlabel('Season', fontsize=14)
            plt.ylabel('Stats Per Game', fontsize=14)
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig(f'nba_player_analysis/player_{player_id}_stats_comparison.png', dpi=300)
            print(f'已保存球員數據對比圖')
        
        # 繪製最近一年的雷達圖
        if 'GP' in season_stats.columns:
            # 取最近參加了20場比賽的年份
            recent_season = season_stats[season_stats['GP'] >= 20].iloc[-1] if not season_stats[season_stats['GP'] >= 20].empty else None
            
            if recent_season is not None and all(col in recent_season.index for col in ['PTS', 'AST', 'REB', 'STL', 'BLK']):
                # 繪製雷達圖的各個特性
                categories = ['Points', 'Assists', 'Rebounds', 'Steals', 'Blocks']
                
                # 最近一年的數據
                values = [
                    recent_season['PTS'],
                    recent_season['AST'],
                    recent_season['REB'],
                    recent_season['STL'],
                    recent_season['BLK']
                ]
                
                # 當前數據與參考數據的對比（以30分、10助攻、15籃板、3搶斷、3蓋帽為參考）
                # 將數據歸一化到0-100之間，以便於比較
                reference = [30, 10, 15, 3, 3]  # 得分、助攻、籃板、搶斷、蓋帽的參考高值
                normalized = [min(v / ref * 100, 100) for v, ref in zip(values, reference)]
                
                # 繪製雷達圖
                angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
                values = normalized + [normalized[0]]  # 將第一個值複製到最後，以形成閉合的多邊形
                angles += angles[:1]  # 將第一個角度複製到最後，以形成閉合的多邊形
                categories += [categories[0]]  # 將第一個類別複製到最後，以形成閉合的多邊形
                
                fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
                ax.plot(angles, values, linewidth=2, linestyle='solid')
                ax.fill(angles, values, alpha=0.25)
                
                # 設置分割線和標籤
                ax.set_thetagrids(np.degrees(angles[:-1]), categories[:-1])
                ax.set_ylim(0, 100)
                ax.set_title(f'{player_name} Recent Season ({recent_season.get("SEASON_ID", "N/A")}) Radar Chart', fontsize=15, y=1.1)
                
                # 在每個扇區中添加數據值
                for i, (angle, value, normalized_value) in enumerate(zip(angles[:-1], values[:-1], [recent_season['PTS'], recent_season['AST'], recent_season['REB'], recent_season['STL'], recent_season['BLK']])):
                    ax.text(angle, value + 10, f'{normalized_value:.1f}', horizontalalignment='center', verticalalignment='center')
                
                plt.tight_layout()
                plt.savefig(f'nba_player_analysis/player_{player_id}_radar_chart.png', dpi=300)
                print(f'已保存球員雷達圖')
        
        return season_stats
    except Exception as e:
        print(f'分析每年數據時出現錯誤: {e}')
        return None

# 生成球员分析报告
def write_player_report(player_id, player_info, career_stats, season_stats):
    player_name = player_info.get('name', f'Player {player_id}') if player_info else f'Player {player_id}'
    
    # 将DataFrame转换为表格
    career_summary = ''
    if career_stats is not None and not career_stats.empty:
        career_row = career_stats.iloc[0] if len(career_stats) > 0 else None
        if career_row is not None:
            career_summary = f'\n职业平均数据:\n'
            if 'GP' in career_row:
                career_summary += f'\n场次: {career_row["GP"]}'
            if 'PTS' in career_row:
                career_summary += f'\n得分: {career_row["PTS"]:.1f}'
            if 'AST' in career_row:
                career_summary += f'\n助攻: {career_row["AST"]:.1f}'
            if 'REB' in career_row:
                career_summary += f'\n篮板: {career_row["REB"]:.1f}'
            if 'STL' in career_row:
                career_summary += f'\n抢断: {career_row["STL"]:.1f}'
            if 'BLK' in career_row:
                career_summary += f'\n盖帽: {career_row["BLK"]:.1f}'
            if 'FG_PCT' in career_row:
                career_summary += f'\n投篮命中率: {career_row["FG_PCT"]*100:.1f}%'
            if 'FG3_PCT' in career_row:
                career_summary += f'\n三分命中率: {career_row["FG3_PCT"]*100:.1f}%'
            if 'FT_PCT' in career_row:
                career_summary += f'\n罚球命中率: {career_row["FT_PCT"]*100:.1f}%'
    
    # 统计最佳的年份得分
    season_trends = ''
    if season_stats is not None and not season_stats.empty and 'PTS' in season_stats.columns:
        max_pts_season = season_stats.loc[season_stats['PTS'].idxmax()]
        if 'SEASON_ID' in max_pts_season and 'PTS' in max_pts_season:
            season_trends += f'\n得分最高: {max_pts_season["SEASON_ID"]} 年份，平均 {max_pts_season["PTS"]:.1f} 分'
    
    # 生成报告
    report = f'''球员分析报告: {player_name}

'''
    
    # 添加球员信息
    if player_info:
        report += '球员信息:\n'
        for key, value in player_info.items():
            report += f'{key.capitalize()}: {value}\n'
    
    # 添加职业平均数据
    report += f'\n{career_summary}'
    
    # 添加年份得分趋势
    report += f'\n{season_trends}'
    
    # 附上图表说明
    report += f'''

附上图表:
1. player_{player_id}_pts_trend.png - 得分趋势图
2. player_{player_id}_stats_comparison.png - 数据对比图
3. player_{player_id}_radar_chart.png - 数据雷达图
'''
    
    # 保存报告到文件
    with open(f'nba_player_analysis/player_{player_id}_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f'已生成球员 {player_name} 的分析报告')
    return report

# 主函数
def main():
    # 检查命令行参数或提示用户输入
    if len(sys.argv) > 1:
        player_id = sys.argv[1]
    else:
        player_id = input('请输入要分析的球员 ID: ')
    
    # 检查必要的目录是否存在
    if not os.path.exists('nba_player_data'):
        print('错误：未找到 nba_player_data 目录。请先运行 player_specific_scraper.py 获取球员数据。')
        return
    
    # 检查球员数据是否存在
    stats_file = f'nba_player_data/player_{player_id}_stats.json'
    info_file = f'nba_player_data/player_{player_id}_info.json'
    
    if not os.path.exists(stats_file) or not os.path.exists(info_file):
        print(f'错误：请先运行 player_specific_scraper.py 获取球员 {player_id} 的数据。')
        return
    
    # 加载统计数据和球员信息
    stats = load_player_stats(player_id)
    player_info = load_player_info(player_id)
    
    if not stats:
        print('无法加载球员统计数据，无法进行分析。')
        return
    
    player_name = player_info.get('name', f'Player {player_id}') if player_info else f'Player {player_id}'
    print(f'开始分析 {player_name} 的数据...')
    
    # 分析职业平均数据
    print('\n分析职业平均数据...')
    career_stats = analyze_career_averages(stats)
    
    # 分析每年表现
    print('\n分析每年表现...')
    season_stats = analyze_season_by_season(stats, player_info, player_id)
    
    # 生成报告
    print('\n生成球员分析报告...')
    write_player_report(player_id, player_info, career_stats, season_stats)
    
    print(f'\n所有分析结果已保存在 nba_player_analysis 目录下。')

if __name__ == '__main__':
    main()