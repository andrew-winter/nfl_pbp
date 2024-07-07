# %%
# Description and modules
"""
The purpose of this program is to demonstrate the 'quick steps' of writing main()
"""
import os
import re
import pandas as pd
WDIR = r'C:\Users\ussoc\Documents\Technical\Python-projects\sports\nfl_basics'
os.chdir(WDIR)

# %%
# Quick steps
def main():
    raw_df = read_pbp_files(end_year=2023, years_prior=10)
    agg_cols = ['yards_gained','pass_attempt','complete_pass','touchdown','interception','passing_yards','rushing_yards','sack','field_goal_attempt']
    df = filter_and_fill(raw_df, fill_nas=agg_cols)
    display_top_recievers(df)

# %%
# Read and concatenate play-by-play files
# Requires os, re, and pandas
def read_pbp_files(end_year=2023, years_prior=3):
    # Iterate years, create a regex pattern
    data_wdir = f'{WDIR}\data\pbp'
    years = [str(yr) for yr in range(end_year - years_prior, end_year + 1)]
    years_concat = '|'.join(years)
    pattern = re.compile(f'.*({years_concat}).*')
    # Read in files using regex, concat into one df
    raw_dfs = []
    for fname in os.listdir(data_wdir):
        if pattern.match(fname):
            try:
                path = os.path.join(data_wdir, fname)
                df = pd.read_csv(path)
                raw_dfs.append(df)
            except:
                pass
    raw_df = pd.concat(raw_dfs, ignore_index=True)
    return raw_df

# %%
# Reduce number of columns, filter for KC offense, fill missing ints
def filter_and_fill(raw_df={}, fill_nas=[]):
    cols = [
        'complete_pass'
        ,'incomplete_pass'
        ,'pass_length'
        ,'receiver'
        ,'receiving_yards'
        ,'pass_attempt'
        ,'passer'
        ,'passing_yards'
        ,'pass'
        ,'rush_attempt'
        ,'rusher'
        ,'rushing_yards'
        ,'rush'

        ,'season', 'season_type', 'week',
        'game_id', 'game_date',
        'qtr', 'down',
        'posteam', 'defteam',

        'touchdown', 'td_team', 'td_player_name',
        'interception', 'sack',
        #'receiver_touchdown',
        'pass_touchdown', 'rush_touchdown',
        'field_goal_attempt', 'field_goal_result', 'kick_distance', 'kicker_player_name',
        'extra_point_attempt', 'extra_point_result', 
        'two_point_attempt', 'two_point_conv_result',
        'kickoff_attempt', 'kickoff_returner_player_name',

        'drive', 'first_down',
        'play_id', 'play_type', 'yards_gained', 'ydstogo',
        'home_team', 'away_team',
        'timeout', 'timeout_team', 'penalty_team']
    kc_offense = raw_df['posteam'] == 'KC'
    filtered_df = (
        raw_df
            .copy()
            [cols]
            .loc[kc_offense])
    filtered_df[fill_nas] = filtered_df[fill_nas].fillna(value=0)
    # Field goal columns?
    filtered_df['field_goals'] = (filtered_df['field_goal_result'] == 'made').astype(int) 
    return filtered_df

# %%
# Aggregate and look at top recievers
def display_top_recievers(df={}):
    metrics = agg_cols + ['field_goals']
    per_game = ['season_type', 'season', 'game_id', 'game_date', 'week']
    per_season = ['season_type', 'season']
    totals_per_game = pd.DataFrame()
    for col in metrics:
        totals_per_game[col] = (
            df
                .groupby(per_game)
                .agg({col: 'sum'}))
    totals_per_game.sort_values('game_id', inplace=True)
    totals_per_game.reset_index(inplace=True)
    print(totals_per_game)


# %%
    


# %%


# %%
# if __name__ == '__main__'
if __name__ == '__main__':
    main()



# %%
