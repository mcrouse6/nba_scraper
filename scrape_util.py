import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
from scipy.stats import zscore
import time
import os

leagueId = 205090
seasonId = 2018
league_url = "http://games.espn.com/fba"

def getStatsByManagerId(teamId):
    html = requests.get("%s/%s?leagueId=%s&teamId=%s&seasonId=%s" % 
                            (league_url, "clubhouse", leagueId, teamId, seasonId))

    soup = BeautifulSoup(html.text)
    stats = soup.find('table', {'id': 'playertable_0'})

    manager_info = soup.find('div', {'class': 'games-univ-mod3'})
    team_name = soup.find('h3', {'class': 'team-name'}).text
    manager_name = manager_info.find('li', {'class': 'per-info'}).text

    columns = ['FGM/FGA', 'FG%','FTM/FTA', 'FT%','3PM','REB', 'AST', 'STL', 'BLK', 'TO','PTS']

    final_columns = ['Manager_id', 'Manager_Name', 'Player', 'FGM', 'FGA', 'FG%', 'FTM', 'FTA', 'FT%', '3PM', 
                    'REB', 'AST', 'STL', 'BLK', 'TO','PTS']


    starter_rows = stats.findAll('tr')[2:10]
    bench_rows = stats.findAll('tr')[-3:]
    player_rows = stats.findAll('tr')
    all_data = []
    for row in player_rows:
        if row.find('a'):
            # print row.find('a').text
            idv_stats = row.find_all('td', {"class": "playertableStat"})
            dat = [teamId, manager_name, row.find('a').text]
            for i, s in enumerate(idv_stats):
                # print s.text
                if columns[i] == "FGM/FGA" or columns[i] == "FTM/FTA":
                    made = s.text.split("/")[0]
                    att = s.text.split("/")[1]
                    if made != "--":
                        dat.append(float(made))
                        dat.append(float(att))
                    else:
                        dat.append(0.0)
                        dat.append(0.0)
                else:
                    if s.text != "--":
                        dat.append(float(s.text))
                    else:
                        dat.append(0.0)
            all_data.append(dat)

    return pd.DataFrame.from_records(all_data, columns=final_columns)

def getAllRosterInfo():
    data = []
    for i in range(14):
        print i
        pf = getStatsByManagerId(i+1)        
        print pf
        data.append(pf)

    result = pd.concat(data)
    directory = "2017-2018_data/fullRosters"
    if not os.path.exists(directory):
        os.makedirs(directory)

    result.to_csv(time.strftime('2017-2018_data/fullRosters/%Y_%m_%d_%H_%M.csv'))
    return result

def getCurrentStandings():
    #http://games.espn.com/fba/standings?leagueId=205090&seasonId=2018

    html = requests.get("%s/%s?leagueId=%s&seasonId=%s" % 
                            (league_url, "standings", leagueId, seasonId))

    soup = BeautifulSoup(html.text)
    master_table = soup.find('table', {'class': 'maincontainertbl'})
    rows = master_table.find_all('tr')[4:]

    cat_list = ['FG%', 'FT%', '3PM', 
                        'REB', 'AST', 'STL', 'BLK', 'TO','PTS']
    summary_info = ['TOTAL', 'PTS_CHANGE']
    other_info = ['GP', 'MOVES_MADE']
    base_info = ['Manager_id', "Manager_Name"]

    all_data = []
    for row in rows:
        # print row.find('a').text
        stats = row.find_all('td')[3:3+len(cat_list)]
        teaminfo = row.find('a')
        name = teaminfo.text
        teamId = int(teaminfo['href'].split('&')[-2].split('=')[1])
        data = [teamId, name]
        for i, stat in enumerate(stats):
            print cat_list[i], stat.text
            data.append(stat.text)

        stats = row.find_all('td')[len(cat_list)+4:]
        for i, stat in enumerate(stats):
            print summary_info[i], stat.text
            data.append(stat.text)
        
        all_data.append(data)

    standings = pd.DataFrame.from_records(all_data, columns=base_info + cat_list + summary_info)
    directory = "2017-2018_data/standings"
    if not os.path.exists(directory):
        os.makedirs(directory)
    standings.to_csv(time.strftime('2017-2018_data/standings/%Y_%m_%d_%H_%M.csv'))

    stats_table = soup.find('table', {'id': 'statsTable'})
    rows = stats_table.find_all('tr')[3:]
    all_data = []
    for row in rows:
        print row.find('a').text
        teaminfo = row.find('a')
        name = teaminfo.text
        teamId = int(teaminfo['href'].split('&')[-2].split('=')[1])
        stats = row.find_all('td')[3:-3]
        data = [teamId, name]
        for i, stat in enumerate(stats):
            print cat_list[i], stat.text
            data.append(stat.text)

        stats = row.find_all('td')[-2:]
        for i, stat in enumerate(stats):
            print other_info[i], stat.text
            data.append(stat.text)
        all_data.append(data)

    stat_summary = pd.DataFrame.from_records(all_data, columns=base_info + cat_list + summary_info)
    directory = "2017-2018_data/summaries"
    if not os.path.exists(directory):
        os.makedirs(directory)
    stat_summary.to_csv(time.strftime('2017-2018_data/summaries/%Y_%m_%d_%H_%M.csv'))

    return standings, stat_summary


active_rosters = getAllRosterInfo()
standings, stat_summary = getCurrentStandings()