# %%
# More streamlined analysis of nflverse pbp once downloaded
import json
import os
import pandas as pd
import re
import requests
import seaborn as sns
from bs4 import BeautifulSoup
#from download_nflverse import download_nflverse
from read_nflverse_dictionary import read_nflverse_dictionary
NFLVERSE_URL = 'https://github.com/nflverse/nflverse-data/releases/download'
WORK_DIRECTORY = os.environ.get('NFLVERSE_PBP_WORKING_DIRECTORY')
DATA_PBP = rf'{WORK_DIRECTORY}\data\pbp'
DATA_PLAYERS = rf'{WORK_DIRECTORY}\data\players'
os.chdir(WORK_DIRECTORY)

# %%
# Identify nflverse fields, data types, players data
data_dictionary = read_nflverse_dictionary()
# Dictionary comprehension to map dtypes to field names
pbp_dtypes = {dy['field']: dy['pdtype'] for dy in data_dictionary.to_dict('records')}
players = pd.read_csv(rf'{DATA_PLAYERS}\players.csv')

# %%
# Concatenate list of seasons data
list_seasons = []
for gm in range(2014, 2024):
    file = os.path.join(DATA_PBP, rf'play_by_play_{gm}.csv')
    list_seasons.append(pd.read_csv(file, dtype=pbp_dtypes))

# %%
# Record passer stats
stats_normal = ['season_type', 'season', 'week', 'game_id']
stats_passer = ['passer_id', 'passer']
stats_rusher = ['rusher_id', 'rusher']
df = pd.DataFrame()
for yr in list_seasons:
    pass_sum = yr.groupby(stats_normal+stats_passer)['passing_yards'].sum()
    pass_att = yr.groupby(stats_normal+stats_passer)['pass_attempt'].sum()
    pass_max = yr.groupby(stats_normal+stats_passer)['passing_yards'].max()
    
    rush_sum = yr.groupby(stats_normal+stats_rusher)['rushing_yards'].sum()
    rush_att = yr.groupby(stats_normal+stats_rusher)['rush_attempt'].sum()
    rush_max = yr.groupby(stats_normal+stats_passer)['rushing_yards'].max()

    df = pd.concat([df, pass_sum, pass_att, pass_max, rush_sum, rush_att, rush_max], ignore_index=True)


# %%
df = pd.DataFrame()
for yr in list_seasons:
    for type in ['pass', 'rush']:
        yards_comp = yr.groupby(stats_normal+[f'{type}ing_yards']).sum().reset_index()
        yards_att = yr.groupby(stats_normal+[f'{type}_attempt']).sum().reset_index()
        yards_max = yr.groupby(stats_normal+[f'{type}ing_yards']).max().reset_index()
        pd.concat(df, yards_comp, yards_att, yards_max, ignore_index=True)




# %%

# %%
range_types = ('passing_yards', 'rushing_yards')
range_stats = ('sum', 'mean', 'max')
for yr in range(len(list_seasons)):
    for ty in range_types:
        for st in range_stats:
            combo = [ty] + [st] + list(list_seasons[yr])
            print(combo)
            #print(list_seasons[yr].groupby(stats_normal+[ty]+[st]))


 # %%
# Iterate through data to map games
list_seasons[1].groupby(['game_id', 'passer_id'])['passing_yards'].sum().reset_index()


# %%

