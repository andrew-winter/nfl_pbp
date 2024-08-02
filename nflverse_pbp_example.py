# %%
# Description, modules, and constants
"""
Update nflverse play-by-play data
"""
import os
from html.parser import HTMLParser
import json
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
W_DIR = r"C:\Users\ussoc\Documents\Technical\Python-projects\sports\nfl_basics"
os.chdir(W_DIR)
NFLVERSE_URL = "https://github.com/nflverse/nflverse-data/releases/download"


# %%
# Function to read URL and download file to destination
def download_nflverse(url: str, fpath: str, sdir: str):
    filename = url.split(f"{sdir}/")[1]
    filepath = os.path.join(fpath, filename)

    r = requests.get(url, stream=True)
    if r.ok:
        print("saving file to:\t", os.path.abspath(filepath))
        with open(filepath, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
            print("file saved", "\n" * 2)


# %%
# Download last 7 years of pbp data
min_year = 2017
max_year = 2023

pbp_dir = rf"{W_DIR}\data\pbp"
pbp_url = f"{NFLVERSE_URL}/pbp/play_by_play"

for yr in range(min_year, max_year + 1):
    download_nflverse(f"{pbp_url}_{yr}.csv", pbp_dir, "pbp")


# %%
# Download player data
players_dir = f"{W_DIR}\data\players"
players_url = f"{NFLVERSE_URL}/players/players"
download_nflverse(f"{players_url}.csv", players_dir, "players")


# %%
# Function to read create nflverse data dictionary
def read_nflverse_dictionary():
    url = "https://nflreadr.nflverse.com/articles/dictionary_pbp.html"
    datatable_class = "datatables html-widget html-fill-item"
    htmlwidget_id = "htmlwidget-ac96cb3ee4656e2e9ec3"
    json_start = '"data":(\[.*\])'
    json_end = ',"container'

    d = requests.get(url)
    soup = BeautifulSoup(d.text, "html.parser")

    # Locate the div with the specific class and id
    content = (
        soup
            .find("div", class_=datatable_class, id=htmlwidget_id)
            .find_next("script")
            .string)
    
    pattern = re.compile(rf'{json_start}{json_end}')
    match = pattern.search(content).group(1)
    json_loads = json.loads(match)
    
    df = pd.DataFrame({
        key: val for (key, val) in zip(["field", "desc", "type"], json_loads)})
    df.loc[df["type"] == "numeric", "pdtype"] = float
    df.loc[df["type"] == "character", "pdtype"] = str

    return df
data_dictionary = read_nflverse_dictionary()


# %%
# Dictionary comprehension to map dtypes to field names
pbp_dtypes = {dy["field"]: dy["pdtype"] for dy in data_dictionary.to_dict("records")}


# %%
# Function to concatenate pbp files
def concat_pbp(min_year: int, max_year: int, dir):
    years = [str(yr) for yr in range(min_year, max_year + 1)]
    pattern = re.compile(f'.*({"|".join(years)})')

    raw_dfs = []
    for fn in os.listdir(dir):
        if pattern.match(fn):
            try:
                df = pd.read_csv(os.path.join(dir, fn), dtype=pbp_dtypes)
                raw_dfs.append(df)
            except:
                pass
    concat_df = pd.concat(raw_dfs, ignore_index=True)
    return concat_df


# %%
# Concatenate pbp data into one DataFrame
raw_pbp = concat_pbp(min_year=2004, max_year=max_year, dir=pbp_dir)


# %%
# Aggregate different stats
#agg_funcs = {stat: ["mean", "max", "min", "count"] for stat in ["passing_yards", "rushing_yards"]}
agg_funcs = {
    "pass_attempt": ["count", "sum"],
    "passing_yards": ["sum", "mean", "max"],
    "rush_attempt": ["count", "sum"],
    "rushing_yards": ["sum", "mean", "max"]
}
pd.pivot_table(raw_pbp,
               values=["pass_attempt", "passing_yards", "rush_attempt", "rushing_yards"],
               index=["season", "game_id"], aggfunc=agg_funcs).reset_index().reset_index()




# %%
# Columns to keep
first_four_cols = ["season", "week", "game_id", "play_id"]
numeric_cols = ["qtr", "drive", "down", "game_seconds_remaining", "quarter_end", "complete_pass", "incomplete_pass", "pass_length", "receiving_yards", "pass_attempt", "passing_yards", "pass", "rush_attempt", "rushing_yards", "rush"]
character_cols = ["passer", "receiver", "rusher", "posteam", "defteam", "season_type", "game_date", "time", "yrdln", "yardline_100", "ydstogo", "yards_gained"]

"""
(
    raw_pbp
        .copy()
        [first_four_cols + numeric_cols + character_cols]
        .sort_values(by=["season", "week", "game_id", "play_id"], ascending=True)
        .to_csv(f"{pbp_dir}\pbp_2004-2023.csv", index=False)
)

kc_offense_bool = raw_pbp["posteam"] == "KC"
kc_offense = (
    raw_pbp
        .copy()
        [first_four_cols + numeric_cols + character_cols]
        .loc[kc_offense_bool]
        .sort_values(by=["season", "week", "game_id", "play_id"], ascending=True))
"""

limited_pbp = (
    raw_pbp
        .copy()
        [first_four_cols + numeric_cols + character_cols]
        #.loc[kc_offense_bool]
        .sort_values(by=["season", "week", "game_id", "play_id"], ascending=True))


# %%



# %%
# Split DataFrame into multiple csv files with row size
n_files = 10
n_rows = (len(limited_pbp.index) / n_files) + 1
 
for file in range(n_files):
    df = limited_pbp.iloc[n_rows * file: n_rows * (file + 1)]
    df.to_csv(rf"C:\Users\ussoc\Documents\Technical\Python-projects\workflows\coalesce\explore\limited_20240801_i{row + 1}.csv", index=False)



# %%
# Save file
limited_pbp.to_csv(r"C:\Users\ussoc\Documents\Technical\Python-projects\workflows\coalesce\explore\raw_20240801_v2.csv", index=False)



# %%
