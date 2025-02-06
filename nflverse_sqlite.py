# %%
# Store nflverse play-by-play and player data in sqlite database
import json
import os
import pandas as pd
import re
import requests
import sqlite3
from bs4 import BeautifulSoup
from download_nflverse import download_nflverse
from read_nflverse_dictionary import read_nflverse_dictionary
NFLVERSE_URL = 'https://github.com/nflverse/nflverse-data/releases/download'
WORK_DIRECTORY = os.environ.get('NFLVERSE_PBP_WORKING_DIRECTORY')
os.chdir(WORK_DIRECTORY)
connection = sqlite3.connect(f'{WORK_DIRECTORY}\data\dbs\pbp.sqlite')

# %%
# Download player data and add to database
dir_players = f'{WORK_DIRECTORY}\data\players'
download_nflverse(f'{NFLVERSE_URL}/players/players', directory=dir_players, label='players')
players = pd.read_csv(rf'{dir_players}\players.csv')
players['last_updated'] = pd.Timestamp.now()
players.to_sql(name='players', con=connection, if_exists='replace')

# %%
# Read in the nflverse pbp data dictionary to convert data types
data_dictionary = read_nflverse_dictionary()
# Dictionary comprehension to map dtypes to field names
pbp_dtypes = {dy['field']: dy['pdtype'] for dy in data_dictionary.to_dict('records')}

# %%
# Download pbp data and add to database
year_min = 2015
year_max = 2024
dir_pbp = f'{WORK_DIRECTORY}\data\pbp'
for yr in range(year_min, year_max + 1):
    download_nflverse(f'{NFLVERSE_URL}/pbp/play_by_play_{yr}.csv', directory=dir_pbp, label='pbp')
    pbp = pd.read_csv(os.path.join(dir_pbp, f'play_by_play_{yr}.csv'), dtype=pbp_dtypes)
    pbp['last_updated'] = pd.Timestamp.now()
    pbp.to_sql(name=f'pbp_{yr}', con=connection)

# %%
