# %% PURPOSE: Explore ML basics with NFL data
import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# %%
# Constants, set working directory
os.chdir(r'C:\Users\ussoc\Documents\Technical\Python-projects\sports\nfl_basics')


# %%
# Just three seasons of data for now
pattern = re.compile(r'.*(2019|2020|2021).*')
raw_files = [f'data\{fn}' for fn in os.listdir('data') if pattern.match(fn)]


# %%
# Concat files
target_files = []
for fn in os.listdir('data'):
    if pattern.match(fn):
        df = pd.read_csv(os.path.join('data', fn))
        target_files.append(df)

raw_df = pd.concat(target_files, ignore_index=True)


# %%
# Look at QB stats
qb_feats = ['season', 'passer_id', 'passer', 'pass', 'complete_pass', 'interception', 'sack', 'yards_gained', 'touchdown']
groupby_feats = ['season', 'passer_id', 'passer']
qb_df = (
    raw_df
        .loc[:, qb_feats]
        .groupby(groupby_feats, as_index=False)
        .sum()
)


# %%
# What correlates with TDs?
corr_feats = ['yards_gained', 'complete_pass', 'pass', 'interception', 'sack']
for ft in corr_feats:
    sns.regplot(data=qb_df, x='touchdown', y=ft)
    plt.title(f'touchdowns and {ft}')
    plt.show()


# %%
# All of these stats appear to correlate with TDs-- what about _next season_ TDs?
_df = qb_df.copy()
_df['season'] = _df['season'].add(1)
new_qb_df = (
    qb_df
        .merge(_df,
            how='left',
            on=['season', 'passer_id', 'passer'],
            suffixes=('', '_prev'))
)
new_qb_df.sample(8)


# %%
# EDA-- Which passers and seasons had low interceptions and high touchdowns
(
    new_qb_df
        .sort_values(
            by=['interception', 'touchdown', 'touchdown_prev'],
            ascending=[True, False, False])
)


# %%
# What correlates with *next season* TDs?
prev_corr_feats = [f'{ft}_prev' for ft in ['touchdown'] + corr_feats]
for ft in prev_corr_feats:
    sns.regplot(data=new_qb_df, x='touchdown', y=ft)
    plt.title(f'touchdowns and {ft}')
    plt.show()


# %%
# Train/test/split codebasics tutorial:  https://www.youtube.com/watch?v=fwY9Qv96DJY
from sklearn.linear_model import LinearRegression 
from sklearn.metrics import mean_squared_error
from scipy.stats import pearsonr


# %%
# Predict 'current' season touchdowns
target = 'touchdown'
features = prev_corr_feats.copy()

qb_model_df = new_qb_df.dropna(subset=features + [target])
train_df = qb_model_df.loc[qb_model_df['season'] == 2020]
test_df = qb_model_df.loc[qb_model_df['season'] == 2021]

model = LinearRegression()
model.fit(train_df.loc[:, features], train_df[target])
predictions = model.predict(test_df.loc[:, features])
# Set index on predictions to match the correct rows
preds = pd.Series(predictions, index=test_df.index, name='preds')
#test_df.loc[:, 'preds'] = preds.values
test_df = test_df.merge(preds, how='left', left_index=True, right_index=True)


# %%
# Examine quality of prediction
rmse = mean_squared_error(test_df[target], test_df['preds']) ** 0.5
r2 = pearsonr(test_df[target], test_df['preds'])[0] ** 2
print(f'rmse:\t{rmse}\nr2:\t{r2}')


# %%
# Visualize the outputs
sns.regplot(data=test_df, x=target, y='preds')
plt.title('touchdown and preditions')
plt.show()


# %%
# Test results
output_df = test_df.copy()
output_df['diff'] = output_df['touchdown'] - output_df['preds']
output_df['diff_pct'] = (
    output_df['diff'] / output_df['preds']
)
output_cols = ['season', 'passer_id', 'passer', 'preds', 'touchdown', 'diff', 'diff_pct']
output = (
    output_df
        .loc[:, output_cols]
        .sort_values(
            by=['diff', 'touchdown', 'preds'],
            ascending=[False, False, False])
        .reset_index(drop=True)
)


# %%
# Overperformed predictions
output.head(15)
# %%
# Underperformed predictions
output.tail(15)



# %%



# %%