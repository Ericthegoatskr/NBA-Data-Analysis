import requests
import time
import json
import os

# u5275u5efau76eeu9304u4f86u5132u5b58u722cu53d6u7684u8cc7u6599
if not os.path.exists('nba_data_json'):
    os.makedirs('nba_data_json')

# u57fau672cu8a2du7f6e
base_url = 'https://www.nba.com'
api_base_url = 'https://stats.nba.com/stats'

# u7528u65bcu767cu9001u8acbu6c42u7684u6a19u982d
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'Referer': 'https://www.nba.com/',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'
}

# u722cu53d6u63a5u53e3u5b9au7fa9
endpoints = {
    'standings': 'leaguestandings',  # u5305u542bu6240u6709u7403u968au6392u540d
    'schedule': '',  # u8cfdu7a0buff0cu9700u8981u55aeu7368u8655u7406
    'players': 'commonallplayers?LeagueID=00&Season=2024-25&IsOnlyCurrentSeason=1',  # u4e0du5305u542bu8a73u7d30u7684u7403u54e1u6578u64da
    'draft_history': 'drafthistory?College=&LeagueID=00&Overall_Pick=&RoundNum=&RoundPick=&Season=&TeamID=0' # u9078u79c0u6b77u53f2
}

# u51fdu6578uff1au722cu53d6APIu6578u64da
def fetch_api_data(endpoint, params=None):
    url = f'{api_base_url}/{endpoint}'
    try:
        print(f'u6b63u5728u722cu53d6 API: {url}')
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            try:
                data = response.json()
                return data
            except ValueError:
                print(f'u7121u6cd5u89e3u6790JSONu6578u64da')
                return None
        else:
            print(f'u8acbu6c42u5931u6557uff0cu72c0u614bu78bc: {response.status_code}')
            return None
    except Exception as e:
        print(f'u722cu53d6u9047u5230u932fu8aa4: {e}')
        return None

# u51fdu6578uff1au8655u7406u7af6u722du9663u5bb9u6578u64da
def fetch_standings():
    data = fetch_api_data(endpoints['standings'])
    if data and 'resultSets' in data:
        standing_data = data['resultSets'][0]
        headers = standing_data['headers']
        rows = standing_data['rowSet']
        
        # u8f49u63dbu70bau66f4u6613u8655u7406u7684u5f62u5f0f
        standings_list = []
        for row in rows:
            team_data = {}
            for i, header in enumerate(headers):
                team_data[header] = row[i]
            standings_list.append(team_data)
        
        # u5132u5b58u8cc7u6599
        with open('nba_data_json/standings.json', 'w', encoding='utf-8') as f:
            json.dump(standings_list, f, ensure_ascii=False, indent=4)
        print('u6210u529fu5132u5b58u7af6u722du9663u5bb9u6578u64da')

# u51fdu6578uff1au8655u7406u8cfdu7a0bu8868
def fetch_schedule():
    # NBA u7684u8cfdu7a0bu8868u53efu80fdu9700u8981u4f7fu7528u4e0du540cu7684 APIu3002u9019u88cfu76f4u63a5u53d6u5f97u4e3bu9801u9762u7684u8cfdu7a0b
    try:
        url = f'{base_url}/schedule'
        print(f'u6b63u5728u722cu53d6u8cfdu7a0bu8868: {url}')
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            # u5132u5b58u539fu59cb HTML
            with open('nba_data_json/schedule_raw.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print('u6210u529fu5132u5b58u8cfdu7a0bu8868HTML')
        else:
            print(f'u8acbu6c42u5931u6557uff0cu72c0u614bu78bc: {response.status_code}')
    except Exception as e:
        print(f'u722cu53d6u8cfdu7a0bu8868u9047u5230u932fu8aa4: {e}')

# u51fdu6578uff1au8655u7406u7403u54e1u8cc7u6599
def fetch_players():
    data = fetch_api_data(endpoints['players'])
    if data and 'resultSets' in data:
        players_data = data['resultSets'][0]
        headers = players_data['headers']
        rows = players_data['rowSet']
        
        # u8f49u63dbu70bau66f4u6613u8655u7406u7684u5f62u5f0f
        players_list = []
        for row in rows:
            player_data = {}
            for i, header in enumerate(headers):
                player_data[header] = row[i]
            players_list.append(player_data)
        
        # u5132u5b58u8cc7u6599
        with open('nba_data_json/players.json', 'w', encoding='utf-8') as f:
            json.dump(players_list, f, ensure_ascii=False, indent=4)
        print('u6210u529fu5132u5b58u7403u54e1u6578u64da')

# u51fdu6578uff1au8655u7406u9078u79c0u6b77u53f2
def fetch_draft_history():
    data = fetch_api_data(endpoints['draft_history'])
    if data and 'resultSets' in data:
        draft_data = data['resultSets'][0]
        headers = draft_data['headers']
        rows = draft_data['rowSet']
        
        # u8f49u63dbu70bau66f4u6613u8655u7406u7684u5f62u5f0f
        draft_list = []
        for row in rows:
            draft_record = {}
            for i, header in enumerate(headers):
                draft_record[header] = row[i]
            draft_list.append(draft_record)
        
        # u5132u5b58u8cc7u6599
        with open('nba_data_json/draft_history.json', 'w', encoding='utf-8') as f:
            json.dump(draft_list, f, ensure_ascii=False, indent=4)
        print('u6210u529fu5132u5b58u9078u79c0u6b77u53f2u6578u64da')

# u51fdu6578uff1au722cu53d6u7403u968au8cc7u6599
def fetch_team_info(team_id):
    endpoint = f'teaminfocommon?TeamID={team_id}&LeagueID=00'
    data = fetch_api_data(endpoint)
    
    if data and 'resultSets' in data:
        team_info = data['resultSets'][0]
        team_stats = data['resultSets'][1] if len(data['resultSets']) > 1 else None
        
        # u6574u7406u7403u968au8cc7u6599
        team_data = {
            'info': {},
            'stats': {}
        }
        
        # u8655u7406u57fau672cu8cc7u6599
        for i, header in enumerate(team_info['headers']):
            if team_info['rowSet'] and len(team_info['rowSet']) > 0:
                team_data['info'][header] = team_info['rowSet'][0][i]
        
        # u8655u7406u7d71u8a08u8cc7u6599
        if team_stats and team_stats['rowSet'] and len(team_stats['rowSet']) > 0:
            for i, header in enumerate(team_stats['headers']):
                team_data['stats'][header] = team_stats['rowSet'][0][i]
        
        # u5132u5b58u8cc7u6599
        with open(f'nba_data_json/team_{team_id}.json', 'w', encoding='utf-8') as f:
            json.dump(team_data, f, ensure_ascii=False, indent=4)
        print(f'u6210u529fu5132u5b58u7403u968a ID {team_id} u7684u8cc7u6599')

# u4e3bu51fdu6578
def main():
    print('u958bu59cbu722cu53d6 NBA u6578u64da...')
    
    # u722cu53d6u6392u540du8cc7u6599
    print('\nu6b63u5728u722cu53d6u6392u540du8cc7u6599...')
    fetch_standings()
    time.sleep(2)  # u907fu514du8acbu6c42u904eu65bcu983bu7e41
    
    # u722cu53d6u8cfdu7a0bu8868
    print('\nu6b63u5728u722cu53d6u8cfdu7a0bu8868...')
    fetch_schedule()
    time.sleep(2)  # u907fu514du8acbu6c42u904eu65bcu983bu7e41
    
    # u722cu53d6u7403u54e1u8cc7u6599
    print('\nu6b63u5728u722cu53d6u7403u54e1u8cc7u6599...')
    fetch_players()
    time.sleep(2)  # u907fu514du8acbu6c42u904eu65bcu983bu7e41
    
    # u722cu53d6u9078u79c0u6b77u53f2
    print('\nu6b63u5728u722cu53d6u9078u79c0u6b77u53f2...')
    fetch_draft_history()
    time.sleep(2)  # u907fu514du8acbu6c42u904eu65bcu983bu7e41
    
    # u722cu53d6u90e8u5206u7403u968au8cc7u6599uff08u7bc4u4f8buff09
    print('\nu6b63u5728u722cu53d6u90e8u5206u7403u968au8cc7u6599...')
    # u5e38u898bu7684u7403u968a ID
    team_ids = [1610612738, 1610612742, 1610612744]  # u7af6u722du9663u5bb9u6578u64dau4e2du53efu4ee5u627eu5230u66f4u591au7684u7403u968a ID
    for team_id in team_ids:
        fetch_team_info(team_id)
        time.sleep(2)  # u907fu514du8acbu6c42u904eu65bcu983bu7e41
    
    print('\nu6240u6709u6578u64dau722cu53d6u5b8cu6210uff01')

if __name__ == '__main__':
    main() 