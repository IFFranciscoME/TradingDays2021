
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: Applications of Genetic Methods for Feature Engineering and Hyperparameter Optimization    -- #
# -- -------- for Neural Networks.                                                                       -- #
# -- script: main.py : python script with the main functionality of the project                          -- #
# -- author: IFFranciscoME - if.francisco.me@gmail.com                                                   -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/IFFranciscoME/GeneticMethods                                         -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

# -- Load other scripts
import functions as fn
import data as dt
import visualizations as vs

# -- Load packages for this script
import numpy as np
import pandas as pd
import ccxt
import seaborn as sns
import matplotlib.pyplot as plt

# Minor adjustments for pandas visualizations
pd.set_option('display.max_rows', None)                # unlimit rows
pd.set_option('display.max_columns', None)             # unlimit cols
pd.set_option('display.width', None)                   # unlimit width display
pd.set_option('display.expand_frame_repr', False)      # expand cols
pd.options.mode.chained_assignment = None              # no index warning

# --------------------------------------------------------------------------------------------- Notebook -- #
# Use ccxt library

# list of available exchanges in ccxt
exchanges = ccxt.exchanges

# Use previously constructed function to fetch historical OHLCV data with CCXT - Binance Public API
# help(dt.ini_binance)
# help(dt.massive_ohlcv)

# --------------------------------------------------------------------------------------------- Notebook -- #
## Get historical OHLC Prices

# Get historical data (previously downloaded - check data.py)
df_data = dt.df_prices

# First 5 elements
# df_data.head(5)

# Last 5 elements
df_data.tail(5)

# General description
data_profile = fn.data_profile(p_data=df_data.copy(), p_type='ohlc', p_mult=1)
print(data_profile)

# --------------------------------------------------------------------------------------------- Notebook -- #
## Visualize data with OHLC Candlestick plot made with plotly

# Plot Financial Timeseries Based Candlesticks (OHLC)
plot_0 = vz.g_ohlc(p_ohlc=df_data)

# interactive plot with plotly (check visualizations.py)
# plot_0.show()

# --------------------------------------------------------------------------------------------- Notebook -- #
## Construct linear features (Autoregressive)

# -- Linear Features Engineering
lin_features = fn.linear_features(p_data=df_data, p_memory=7, p_target='co')

# data profile
lin_features_profile = fn.data_profile(p_data=lin_features.copy(), p_type='ts', p_mult=1)

# description 
print(lin_features_profile)

# --------------------------------------------------------------------------------------------- Notebook -- #
## Scale linear features (robust)

# -- Linear Features Scaling
lin_features = fn.data_scaler(p_data=lin_features, p_trans='standard')

# data profile
lin_features_profile = fn.data_profile(p_data=lin_features.copy(), p_type='ts', p_mult=1)
# description 
print(lin_features_profile)

# --------------------------------------------------------------------------------------------- Notebook -- #
## Use gplearn library

# --------------------------------------------------------------------------------------------- Notebook -- #
## Parameters for Symbolic Variable Generation Through Genetic Programming

# 'population': 15000, 'tournament': 2000, 'hof': 30, 'generations': 9, 'n_features': 20,

# paremeters for symbolic features generation process
symbolic_params = {'functions': ['sub', 'add', 'inv', 'mul', 'div', 'abs', 'log', 'sqrt'],
                   'population': 12000, 'tournament': 3000, 'hof': 30, 'generations': 5, 'n_features': 30,
                   'init_depth': (4, 10), 'init_method': 'half and half', 'parsimony': 0.001,
                   'constants': None,
                   'metric': 'pearson', 'metric_goal': 0.90, 
                   'prob_cross': 0.4, 'prob_mutation_subtree': 0.5,
                   'prob_mutation_hoist': 0.05, 'prob_mutation_point': 0.05,
                   'max_samples': 1,
                   'verbose': True, 'parallelization': True, 'warm_start': True}

# --------------------------------------------------------------------------------------------- Notebook -- #
## Symbolic Features Engineering with Genetic Programming

# Target variable name
y_hat = 'co'

# Run process
genetic_prog = fn.genetic_programed_features(p_data=lin_features, p_target=y_hat, p_params=symbolic_params)

# Process description
sym_process = pd.DataFrame(genetic_prog['sym_data']['details'])


# --------------------------------------------------------------------------------------------- Notebook -- #
## Some special notes on this use case of gplearn

# fitness is a demean value transformation in gplearn, calculate .corr() to have original pearson value

# 'best_oob_fitness' == Out-of-bag error for best individual (not applicable for SymbolicTransformer)

# The sum of p_crossover, p_subtree_mutation, p_hoist_mutation and p_point_mutation should total to 1.0

# is possible to have repeated elements (symbolic features) because: low generations mostly

# to get some properties like raw_fitness_ and fitness_ which allow you to get the raw fitness and fitness
#   (regularized by length) for each program

# max_samples not recomended for timeseries it does shuffle data
# warm_start = True for continuing evolution and not loose previous generation

# --------------------------------------------------------------------------------------------- Notebook -- #
## Get info of best programms

# best programs
best_progs = genetic_prog['sym_data']['best_programs']
best_progs

# --------------------------------------------------------------------------------------------- Notebook -- #
## Get info of best features

# symbolic features
sym_features = genetic_prog['sym_features']

# Feature description
# sym_features.describe()

# --------------------------------------------------------------------------------------------- Notebook -- #
## EXPERIMENT 1: Just Symbolic Features

exp_1 = sym_features.copy()
exp_1[y_hat] = lin_features[y_hat].copy()
exp_1 = exp_1.reindex(columns=sorted(list(exp_1.columns)))

# Data for Experiment 3
# exp_1.head()

# correlation matrix
exp_corr_p = exp_1.corr('pearson')
exp_corr_s = exp_1.corr('pearson')

# Plots generation 
plot_1_p = vz.g_heat_corr(p_data=exp_corr_p, p_double=False)
plot_1_s = vz.g_heat_corr(p_data=exp_corr_s, p_double=False)

# show plot
# plot_1_p.show()

# --------------------------------------------------------------------------------------------- Notebook -- #
## EXPERIMENT 2: Original Data and Symbolic Features

exp_2 = pd.concat([lin_features.copy(), sym_features.copy()], axis=1)
# Data for Experiment 3
exp_2.head()

# correlation matrix
exp_corr = exp_2.corr('pearson')
exp_corr_t = exp_corr.where(np.tril(np.ones(exp_corr.shape)).astype(np.bool_))

corr_1 = vz.g_heat_corr(p_data=exp_corr, p_double=False)

# plot 2
plt.figure(figsize=(18, 18))
sns.heatmap(exp_corr_t, cmap='Blues', cbar=True, square=True, center=0.0,
            annot=False, cbar_kws={'shrink':.95}, fmt='.2f')

# formatting
plt.rcParams["xtick.labelcolor"] = 'darkgrey'
plt.rcParams["ytick.labelcolor"] = 'darkgrey'
plt.rcParams["ytick.labelsize"] = 8
plt.rcParams["xtick.labelsize"] = 8

# show plot
# plt.show()

# --------------------------------------------------------------------------------------------- Notebook -- #
## EXPERIMENT 3: Just 'important' variables from Original Data & Symbolic Features

# get all the data (linear features and symbolic features)
exp_3 = exp_2.copy()

# Correlation with target variable most be >= condition_1 
condition_1 = 0.10

# Absolute correlation among all variables most be <= condition_2
condition_2 = 0.5

# Correlation matrix
exp_3_corr = exp_3.corr('pearson')

no_ok_1 = list(exp_3.columns[abs(exp_3_corr[y_hat]) < condition_1])
exp_3_1 = exp_3.drop(no_ok_1, inplace=False, axis=1)

# Sub correlation matrix
exp_3_1_corr = exp_3_1.corr('spearman')

# Drop row and column name like target
exp_3_1_corr.drop(labels=y_hat, axis=0, inplace=True)
exp_3_1_corr.drop(labels=y_hat, axis=1, inplace=True)

# Transform to 1 all the elements below diagnoal and select the ones below the condition_2
upper_tri = exp_3_1_corr.where(np.triu(np.ones(exp_3_1_corr.shape), k=1).astype(bool))
no_ok_2 = [column for column in upper_tri.columns if any(abs(upper_tri[column]) > condition_2)]

exp_3_1_corr.drop(labels=no_ok_2, axis=0, inplace=True)
exp_3_1_corr.drop(labels=no_ok_2, axis=1, inplace=True)
exp_3_2_corr = exp_3_1_corr

# The most correlated to the target and the least correlated to each other 
exp_3 = exp_3[['co'] + list(exp_3_2_corr.columns)]

# Data for Experiment 3
# exp_3.head()

# --------------------------------------------------------------------------------------------- Notebook -- #
### Correlation heatmaps

# layout grid
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18,18))
# calculation for plot 1
exp_corr = exp_3.corr('pearson')
exp_corr_t = exp_corr.where(np.tril(np.ones(exp_corr.shape)).astype(np.bool_))
# plot 1
sns.heatmap(exp_corr_t, cmap='Blues', cbar=False, square=True, ax=ax1, 
            annot=True, annot_kws={'fontsize':8}, fmt='.2f')
ax1.set_title("|Pearson Correlation| > 0.10")

# calculation for plot 2
exp_corr = exp_3.corr('spearman')
exp_corr_t = exp_corr.where(np.tril(np.ones(exp_corr.shape)).astype(np.bool_))
# plot 2
sns.heatmap(exp_corr_t, cmap='Blues', cbar=False, square=True, ax=ax2, 
            annot=True, annot_kws={'fontsize':8}, fmt='.2f')
ax2.set_title("|spearman Correlation| < 0.50")

# formatting
plt.rcParams["xtick.labelcolor"] = 'darkgrey'
plt.rcParams["ytick.labelcolor"] = 'darkgrey'
plt.rcParams["ytick.labelsize"] = 8
plt.rcParams["xtick.labelsize"] = 8

# show plot
# plt.show()

# --------------------------------------------------------------------------------------------- Notebook -- #
## EXPERIMENT 4: top 10 'important' variables (original + symbolic) both using pearson and spearman

# get all the data (linear features and symbolic features)
exp_4 = exp_2.copy()
# Top N important variables (pearson and spearman)
n_important = 10
# use pearson coefficient
exp_4_p = exp_4.corr('pearson')
# use spearman coefficient
exp_4_s = exp_4.corr('spearman')
# create dataframes with top N features according to correlation criteria
exp_4_p = exp_4.copy()[abs(exp_4_p['co']).sort_values(ascending=False)[1:n_important].index]
exp_4_s = exp_4.copy()[abs(exp_4_s['co']).sort_values(ascending=False)[1:n_important].index]
exp_4 = pd.concat([exp_4 ['co'], exp_4_s, exp_4_p], axis=1)
# print top 5 rows
# exp_4.head()

# --------------------------------------------------------------------------------------------- Notebook -- #
### Correlation heatmaps

# layout grid
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14,14))
# calculation for plot 1
exp_corr = exp_4.corr('pearson')
exp_corr_t = exp_corr.where(np.tril(np.ones(exp_corr.shape)).astype(np.bool_))
# plot 1
sns.heatmap(exp_corr_t, cmap='Blues', cbar=False, square=True, ax=ax1, 
            annot=True, annot_kws={'fontsize':8}, fmt='.2f')
ax1.set_title("Pearson Correlation")

# calculation for plot 2
exp_corr = exp_4.corr('spearman')
exp_corr_t = exp_corr.where(np.tril(np.ones(exp_corr.shape)).astype(np.bool_))
# plot 2
sns.heatmap(exp_corr_t, cmap='Blues', cbar=False, square=True, ax=ax2, 
            annot=True, annot_kws={'fontsize':8}, fmt='.2f')
ax2.set_title("spearman Correlation")

# formatting
plt.rcParams["xtick.labelcolor"] = 'darkgrey'
plt.rcParams["ytick.labelcolor"] = 'darkgrey'
plt.rcParams["ytick.labelsize"] = 8
plt.rcParams["xtick.labelsize"] = 8

# show plot
# plt.show()

# --------------------------------------------------------------------------------------------- Notebook -- #
## Models

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import SGD
from sklearn.metrics import r2_score

experiments = {1: exp_1, 2: exp_2, 3: exp_3, 4: exp_4}
exp = 4

data = fn.data_split(p_data=experiments[exp], p_target='co', p_split=0.8)
x_train = data['train_x']
x_val = data['val_x']
y_train = data['train_y']
y_val = data['val_y']

learning_rate = 0.001
epochs = 500
batch = 16
neurons = x_train.shape[1]

# Neural network architecture
model = Sequential()
model.add(Dense(neurons, activation='sigmoid', input_dim=x_train.shape[1]))
model.add(Dense(neurons, activation='sigmoid'))
model.add(Dense(1, activation='linear'))
opt = SGD(lr=learning_rate)

model.compile(loss = 'mean_squared_error', optimizer=opt, metrics=['mse'])

# fit the model
model_history = model.fit(x_train, y_train, epochs=epochs, batch_size=batch,
                        validation_data=(x_val, y_val), verbose=2)

model_score_t = model.evaluate(x_train, y_train)
model_score_v = model.evaluate(x_val, y_val)

print('Train loss:', model_score_t[0])
print('Train mse:', model_score_t[1])
print('Val loss:', model_score_v[0])
print('Val mse:', model_score_v[1])

fig, ax = plt.subplots(1, 1, figsize=(10,6))
ax.plot(model_history.history['loss'], 'r', label='train')
ax.plot(model_history.history['val_loss'], 'b' ,label='val')
ax.set_xlabel(r'Epoch', fontsize=20)
ax.set_ylabel(r'Loss', fontsize=20)
ax.legend()
ax.tick_params(labelsize=20)

y_hat = model.predict(x_train)
R2_score = r2_score(y_train, y_hat)
y_hat_val = model.predict(x_val)
R2_score_val = r2_score(y_val, y_hat_val)

x_min, x_max = min(y_train),max(y_train)
x_line = np.linspace(x_min, x_max)

fig = plt.figure(figsize=(10,6))
plt.scatter(y_train,y_hat,label='Train Estimation')
plt.plot(x_line, x_line, 'k--', label='Perfect estimation')
plt.xlabel('Real output', fontsize=20)
plt.ylabel('Estimation output', fontsize=20)
plt.title('R^2=%0.4f'%R2_score, fontsize=20)
plt.legend()
plt.grid()
plt.show()

x_min, x_max = min(y_train),max(y_train)
x_line = np.linspace(x_min, x_max)

fig = plt.figure(figsize=(10,6))
plt.scatter(y_val, y_hat_val,label='Test Estimation')
plt.plot(x_line, x_line, 'k--', label='Perfect estimation')
plt.xlabel('Real output', fontsize=20)
plt.ylabel('Estimation output', fontsize=20)
plt.title('R^2=%0.4f'%R2_score_val, fontsize=20)
plt.legend()
plt.grid()
plt.show()
