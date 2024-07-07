# %%
# Description, modules, and constants
"""
Update nflverse play-by-play data
"""
import os
import re
import requests
import pandas as pd
WDIR = r"C:\Users\ussoc\Documents\Technical\Python-projects\sports\nfl_basics"
os.chdir(WDIR)


# %%
# Function to read URL and download file to destination
def download_pbp(url: str, dest: str):
    filename = url.split("pbp/")[1]
    filepath = os.path.join(dest, filename)

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
# Download last 10 years of pbp data
base_pbp_url = "https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play"
end_year = 2023
years_prior = 9
data_dir = f"{WDIR}\data\pbp"
for yr in range(end_year - years_prior, end_year + 1):
    download_pbp(f"{base_pbp_url}_{yr}.csv", data_dir)


# %%
# Function to concatenate pbp files
def concat_pbp(end_year=2023, years_prior=9, dir=data_dir):
    years = [str(yr) for yr in range(end_year - years_prior, end_year + 1)]
    pattern = re.compile(f".*({'|'.join(years)})")

    raw_dfs = []
    for fn in os.listdir(dir):
        if pattern.match(fn):
            try:
                df = pd.read_csv(os.path.join(dir, fn))
                raw_dfs.append(df)
            except:
                pass
    concat_df = pd.concat(raw_dfs, ignore_index=True)
    return concat_df


# %%
# Concatenate pbp data into one DataFrame
raw_df = concat_pbp(end_year=2023, years_prior=9, dir=data_dir)


# %%
# Check DataFrame size
n_bytes = raw_df.memory_usage(deep=True).sum()
n_kbs = n_bytes / 1024
n_mbs = n_kbs / 1024
n_gbs = n_mbs / 1024
n_gbs


# %%
# nflversedata dictionary
# https://nflreadr.nflverse.com/articles/dictionary_pbp.html






