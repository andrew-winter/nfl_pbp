# %% Build a ML model looking at the past 8 years of data
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
# Past eight seasons through 2023 Week 12
years = [str(yr) for yr in range(2023 - 8, 2023 + 1)]
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
# Choice columns
offense_cols = ['yards_gained', 'touchdown', 'interception']
defense_cols = ['sack']
receive_cols = ['receiver_id', 'receiver']
pass_cols = ['pass', 'complete_pass', 'pass_length', 'passer_id', 'passer']
team_cols = ['away_team', 'home_team', 'posteam', 'defteam']
info_cols = ['away_coach', 'home_coach', 'game_date']
cols = (
    ['season'] + offense_cols + defense_cols
    + pass_cols + receive_cols
    + team_cols + info_cols)
raw_df[cols].sample(25)


# %%
# Receiver stats, add previous season cols
rec_feats = ['season'] + receive_cols + offense_cols
groupby_feats = ['season'] + receive_cols
rec_df = (
    raw_df
        .loc[:, rec_feats]
        .groupby(groupby_feats, as_index=False)
        .sum())

# Add previous season stats
_df = rec_df.copy()
_df['season'] = _df['season'].add(1)
new_rec_df = (
    rec_df
        .merge(_df,
            how='left',
            on=['season'] + receive_cols,
            suffixes=('', '_prev')))
new_rec_df.sample(20)

# %%
# EDA-- Which receievers in which seasons had high touchdowns and a lot of yards?
(
    new_rec_df
        .sort_values(
            by=['touchdown', 'touchdown_prev', 'yards_gained', 'yards_gained_prev'],
            ascending=[False] * 4)
        .head(15)
)

# %%
# What correlates with receievers' next season TDs?
target = 'touchdown'
features = []#['season'] + receive_cols
for ft in offense_cols:
    prev_ft = f'{ft}_prev'
    features.append(prev_ft)
    sns.regplot(data=new_rec_df, x=target, y=prev_ft)
    plt.title(f'touchdowns and {prev_ft}')
    plt.show()

# %%
# ML packages
from sklearn.linear_model import LinearRegression 
from sklearn.metrics import mean_squared_error
from scipy.stats import pearsonr

# %%
# Predict receivers' 'current' season touchdowns
rec_model_df = (
    new_rec_df
        .dropna(subset=features + [target]))
train_years = [int(yr) for yr in years if '2023' not in yr]
train_df = rec_model_df.loc[rec_model_df['season'].isin(train_years)]
test_df = rec_model_df.loc[rec_model_df['season'] == 2023]


model = LinearRegression()
# model.fit(x, y)
model.fit(train_df.loc[:, features], train_df[target])
predictions = model.predict(test_df.loc[:, features])
# Set index on predictions to match the correct rows
preds = pd.Series(predictions, index=test_df.index, name='preds')
test_df = test_df.merge(preds, how='left', left_index=True, right_index=True)

# Examine quality of prediction
rmse = mean_squared_error(test_df[target], test_df['preds']) ** 0.5
r2 = pearsonr(test_df[target], test_df['preds'])[0] ** 2
print(f'rmse:\t{rmse}\nr2:\t{r2}')

# %%
# Visualize the predictions
sns.regplot(data=test_df, x=target, y='preds')
plt.title('touchdown and predictions')
plt.show()

# %%
# Test results
output_df = test_df.copy()
output_df['diff'] = output_df['touchdown'] - output_df['preds']
output_df['diff_pct'] = output_df['diff'] / output_df['preds']
output_cols = [
    'season', 'receiver', 'yards_gained_prev', 'touchdown_prev',
    'preds', 'touchdown', 'diff', 'yards_gained']
output = (
    output_df
        .loc[:, output_cols]
        .sort_values(
            by=['diff', 'touchdown', 'preds'],
            ascending=[False, False, False])
        .reset_index(drop=True)
)
output

# %%
# Relatively overperformed previous year
output.head(15)
# %%
# Relatively underperformed previous year
output.tail(15)


# %%
# New model
model2 = LinearRegression()
x2 = train_df.loc[:, features]
y2 = train_df[target]
# Since we pulled in every year, does are we using every year's previous features to predict this year's?
model2.fit(x2, y2)
predictions2 = model2.predict(test_df.loc[:, features])
# Set index on predictions to match the correct rows
preds2 = pd.Series(predictions2, index=test_df.index, name='preds')
test_df2 = test_df.merge(preds2, how='left', left_index=True, right_index=True)

# Examine quality of prediction
rmse2 = mean_squared_error(test_df2[target], test_df2['preds']) ** 0.5
r22 = pearsonr(test_df2[target], test_df2['preds'])[0] ** 2
print(f'rmse:\t{rmse2}\nr2:\t{r22}')



# %%


# %%


# %%


# %%

# %%