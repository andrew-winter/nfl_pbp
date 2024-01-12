# %% Check how many Chiefs first down plays result in three or fewer yards
import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# %%
# Set working directory, constants
wdir = r'C:\Users\ussoc\Documents\Technical\Python-projects\sports\nfl_basics'
os.chdir(wdir)
data_wdir = f'{wdir}\data'
# Past five seasons through 2023 Week 15
years = [str(yr) for yr in range(2023 - 5, 2023 + 1)]
years_str = '|'.join(years)
pattern = re.compile(f'.*({years_str}).*')

# %%
# Read in files, concatenate
raw_dfs = []
for fname in os.listdir(data_wdir):
    if pattern.match(fname):
        path = os.path.join(data_wdir, fname)
        df = pd.read_csv(path)
        raw_dfs.append(df)
raw_df = pd.concat(raw_dfs, ignore_index=True)

# %%
# Narrow down columns
ref_cols = [
    'season', 'season_type', 'week',
    'game_id', 'game_date',
    'qtr', 'down',
    'posteam', 'defteam',
    'drive', 'first_down',
    'play_id', 'play_type', 'yards_gained', 'ydstogo',
    'home_team', 'away_team',
    'timeout', 'timeout_team', 'penalty_team'
]


# %%
# Filter for first downs
#kc_offense = raw_df['posteam'] == 'KC'
first_down = raw_df['down'] == 1
df = (
    raw_df
        .copy()
        [ref_cols]
        .loc[first_down]
)
original_df = df.copy()
# %%
# Group plays into ranges of yards gained
yards_gained_bins = [-float('inf'), 0, 4, 10, float('inf')]
yards_gained_labs = ['loss', '0-3', '4-9', '10+']

df['yards_range'] = (
    pd.cut(
        df['yards_gained'],
        bins=yards_gained_bins, 
        labels=yards_gained_labs,
        include_lowest=True, right=False)
)

# Calculate distribution within each range
df['yards_range'].value_counts().sort_index()

# %%
# Overall yards range per season
yard_range_per_season = (
    df
        .groupby(['season', 'yards_range'])
        .size()
        .unstack(fill_value=0)
)
yard_range_per_season
# %%
# Example scatterplot, good place to visualize
#sns.boxplot(data=df, x='season', y='yards_gained')
#plt.title(f'seasons and yards gained')
#plt.show()


# %%
# Check for NaNs



# %%
# Little formatting for first down analysis
df.rename(
    columns={'posteam': 'team', 'game_id': 'games', 'play_id': 'first_downs'},
    inplace=True
)


# %%
# Reference games and first downs per team per season
groupby_labs = ['team', 'season', 'season_type']
groupby_index = (
    pd.MultiIndex.from_product(
        [df[col].unique() for col in groupby_labs],
        names=groupby_labs)
)
groupby_combos = pd.DataFrame(index=groupby_index).reset_index()

games_per_season = df.groupby(groupby_labs)['games'].nunique().reset_index()
plays_per_season = df.groupby(groupby_labs)['first_downs'].nunique().reset_index()

first_downs = (
    groupby_combos
        .merge(games_per_season, how='left', on=groupby_labs)
        .merge(plays_per_season, how='left', on=groupby_labs)
        .fillna(0)
)

# %%
# Examine yards range per team per season per season_type
yards_range = (
    df
        .groupby(groupby_labs + ['yards_range'])
        .size()
        .unstack(fill_value=0)
        .merge(first_downs, how='left', on=groupby_labs)
        .sort_values(
            by=['first_downs', 'games', 'team', 'season_type', 'season'],
            ascending=[False, False, True, False, True])
        .reset_index(drop=True)
)



# %%
# Add stats absolute + percentage of first downs that result in a loss up to thre eyards
yards_range['three_yds_or_less'] = yards_range['loss'] + yards_range['0-3']
yards_range['three_yds_or_less_pct'] = (
    yards_range['three_yds_or_less'] / yards_range['first_downs']
)

# %% 
# 2023 season example
(yards_range
    .sort_values(by=['three_yds_or_less', 'games'], ascending=[False, False])
    .loc[(yards_range['season'] == 2023)
         & (yards_range['season_type'] == 'REG')]
)

# %%

# %%
# Prep data to visualize for 2023 playoff teams
afc_playoffs = ['BAL', 'BUF', 'KC', 'HOU', 'CLE', 'MIA', 'PIT']
nfc_playoffs = ['SF', 'DAL', 'DET', 'TB', 'PHI', 'LA', 'GB']
playoff_teams = afc_playoffs + nfc_playoffs
#playoff_teams = yards_range['team'].isin(afc_playoffs + nfc_playoffs)
viz_df = (
    yards_range
        .copy()
        .loc[(yards_range['team'].isin(playoff_teams))
             & (yards_range['season'] == 2023)
             & (yards_range['season_type'] == 'REG')]
)
viz_df


# %%
# Viz second try
viz_cols = ['three_yds_or_less', '4-9', '10+']
viz_labs = ['loss-3 yards', '4-9 yards', '10+ yards']
viz_vars = viz_df[viz_df.columns.intersection(viz_cols)].loc[:, viz_cols]

team_palette = {
    'PIT': '#FFB612', 'GB': '#203731', 'DET': '#0076B6',
    'SF': '#AA0000', 'MIA': '#008E97', 'BUF': '#00338D',
    'HOU': '#03202F', 'LA': '#003594', 'TB': '#D50A0A',
    'BAL': '#241773', 'PHI': '#004C54', 'DAL': '#041E42',
    'KC': '#E31837', 'CLE': '#FF3C00',
}

sns.set_theme(style='darkgrid')
pair_grid = sns.PairGrid(
    viz_df.sort_values('three_yds_or_less', ascending=True),
    x_vars=viz_vars,
    y_vars=['team'],
    height=7.5, aspect=0.325
)
# Dot plot using stripplot
for tm, var in enumerate(viz_vars.columns):
    pair_grid.map(
        sns.stripplot, size=20, orient='h', jitter=False,
        palette=team_palette,
        linewidth=1, edgecolor='w')

# Use the same x axis limits on all columns and add better labels
pair_grid.set(xlim=(0, 350), xlabel='', ylabel='')

# Bold x-axis labels
for ax in pair_grid.axes.flat:
    ax.set_xlabel(ax.get_xlabel(), fontweight='bold')

fig = pair_grid.fig
fig.suptitle('First downs by range of yards gained - 2023 regular season', y=1.06, fontsize=16, fontweight='bold')


for ax, lab in zip(pair_grid.axes.flat, viz_labs):
    # Set a different title for each axes
    ax.set(title=lab)

    # Make the grid horizontal instead of vertical
    ax.xaxis.grid(False)
    ax.yaxis.grid(True)

# Add annotations
data_source = 'Source: https://github.com/nflverse/nflverse-data/releases/tag/pbp'
annotations = [(data_source, (0.5, 0.02))]
for annotation, coords in annotations:
    fig.text(coords[0], coords[1], annotation, ha='center', va='center', fontsize=12, color='black')

sns.despine(left=True, bottom=True)
plt.show()


# %%
# Check KC first downs with a negative yards gained in 2018 REG
# 38 seems high


# Check KC first downs with 31+ yards_gained in 2020 POST
# 3 seems high

# Check KC first downs overall in 2020 POST AND 2019 POST
# 100

# %% Check KC first down plays


# %%