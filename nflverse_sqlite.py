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
connection = sqlite3.connect(f'{WORK_DIRECTORY}\data\dbs\pbp_1999-2024.sqlite')

# %%
# Download player data and add to database
dir_players = f'{WORK_DIRECTORY}\data\players'
download_nflverse(f'{NFLVERSE_URL}/players/players', directory=dir_players, label='players')
players = pd.read_csv(rf'{dir_players}\players.csv')
players['last_updated'] = pd.Timestamp.now()
players.to_sql(name='players', con=connection, if_exists='fail')

# %%
# Read in the nflverse pbp data dictionary to convert data types
data_dictionary = read_nflverse_dictionary()
# Dictionary comprehension to map dtypes to field names
pbp_dtypes = {dy['field']: dy['pdtype'] for dy in data_dictionary.to_dict('records')}
data_dictionary.to_sql(name='data_dictionary', con=connection, if_exists='fail')

# %%
# Download pbp data and add to database
year_min = 1999
year_max = 2024
dir_pbp = f'{WORK_DIRECTORY}\data\pbp'
for yr in range(year_min, year_max + 1):
    download_nflverse(f'{NFLVERSE_URL}/pbp/play_by_play_{yr}.csv', directory=dir_pbp, label='pbp')
    pbp = pd.read_csv(os.path.join(dir_pbp, f'play_by_play_{yr}.csv'), dtype=pbp_dtypes)
    pbp['last_updated'] = pd.Timestamp.now()
    pbp.to_sql(name=f'pbp_{yr}', con=connection, if_exists='fail')

# %%
query_players = f"""
    SELECT
        display_name
        ,college_name
        ,college_conference
        ,entry_year
        ,date(birth_date) AS birth_date
        ,draft_number
        ,draftround
    FROM players
    WHERE
        date(birth_date) BETWEEN '1995-01-01' AND '1995-12-31'
"""
pd.read_sql(query_players, connection)


# %%

# %%
query_pbp_example = f"""
    SELECT
        *
    FROM pbp_2024
"""
pd.read_sql(query_pbp_example, connection)

# %%
