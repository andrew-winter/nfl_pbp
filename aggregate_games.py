# %% Create tools to aggregate games from pbp data
import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# %%
#ref_cols.extend(['interception', 'sack'])


# %%
df = (
    raw_df
        .copy()
        .loc[
            :,
            ref_cols]
)


# %%
# Fill NaNs
agg_cols = ['pass_attempt', 'complete_pass', 'touchdown',
            'passing_yards', 'rushing_yards',
            'field_goal_attempt', 'field_goal_result',
            'interception', 'sack']
df[agg_cols] = df[agg_cols].fillna(value=0)


# %%
# Add columns to separate game_id by offense and defense
df[['posteam', 'defteam']] = df[['posteam', 'defteam']].fillna(value='')
df['game_id_pos'] = df['game_id'] + '-' + df['posteam']
df['game_id_def'] = df['game_id'] + '-' + df['defteam']


# %%
# Example-- rows where the td_team is not on offense
df.loc[
    (~df['td_team'].isna())
    & (df['posteam'] != df['td_team'])
    & (df['game_id'].str.contains('2023.*KC', regex=True)),
    ['game_id', 'touchdown', 'posteam', 'td_team']
]


# %%
# Add a defensive touchdown column
defensive_touchdowns = (
    (~df['td_team'].isna())
    & (df['posteam'] != df['td_team']))
df.loc[defensive_touchdowns, 'def_td'] = df['touchdown']
df.loc[defensive_touchdowns, 'touchdown'] = 0


# %%
# Aggregated KC 2023 games
# Regex doesn't have to be this specific, just for demonstration
kc_2023_regex = '2023_\d{2}_.*-KC'
kc_2023_bool = df['game_id_pos'].str.contains(kc_2023_regex, regex=True)
kc_2023 = pd.pivot_table(
    data=df.loc[kc_2023_bool],
    index='game_id_pos',
    values=['def_td'] + agg_cols,
    aggfunc='sum')
reordered_cols = [
    'complete_pass', 'pass_attempt',
    'passing_yards', 'rushing_yards',
    'field_goal_result',
    'touchdown', 'interception', 'def_td']
kc_2023.loc[:, reordered_cols].sort_values(by='game_id_pos', ascending=False)


# %%
# Are there missing values for posteam and defteam?
df.loc[df['game_id'] == '2023_20_KC_BUF'].value_counts(['defteam'], dropna=False)
# Why are the defteam and posteam counts of plays the same for different teams?
# Because when one team is on offense the other team is necessarily on defense, duh



# %%
df.loc[
    df['game_id'].str.contains('2023_20')
    & df['field_goal_attempt'] == 1]


# %%
df.loc[df['game_id'].str.contains('2023_19')].value_counts(['defteam'], dropna=False)


# %%
