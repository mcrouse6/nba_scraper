import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
from scipy.stats import zscore
import time

leagueId = 205090
seasonId = 2018
league_url = "http://games.espn.com/fba"

def getManagerStats(teamId):
    html = requests.get("%s/%s?leagueId=%s&teamId=%s&seasonId=%s" % 
                            (league_url, "clubhouse", leagueId, teamId, seasonId))

    soup = BeautifulSoup(html.text)
    stats = soup.find('table', {'id': 'playertable_0'})

    columns = ['FGM/FGA', 'FG%','FTM/FTA', 'FT%','3PM','REB', 'AST', 'STL', 'BLK', 'TO','PTS']

    final_columns = ['Manager_id', 'Player', 'FGM', 'FGA', 'FG%', 'FTM', 'FTA', 'FT%', '3PM', 
                    'REB', 'AST', 'STL', 'BLK', 'TO','PTS']


    starter_rows = stats.findAll('tr')[2:10]
    bench_rows = stats.findAll('tr')[-3:]
    player_rows = stats.findAll('tr')
    all_data = []
    for row in player_rows:
        if row.find('a'):
            # print row.find('a').text
            idv_stats = row.find_all('td', {"class": "playertableStat"})
            dat = [teamId, row.find('a').text]
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

data = []
for i in range(14):
    print i
    pf = getManagerStats(i+1)        
    print pf
    data.append(pf)

result = pd.concat(data)
result.to_csv(time.strftime('2017-2018_data/%Y_%m_%d_%H_%M.csv'))