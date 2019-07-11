# -*- coding: utf-8 -*-
"""
Created on Sun Jul  7 20:22:48 2019

@author: yiannisPC
"""
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import lightgbm as lgb
from sklearn.metrics import mean_squared_error, auc, roc_curve, accuracy_score
import matplotlib.pyplot as plt

#data_df = pd.read_csv("data.csv", index_col=0, 
#                      dtype={"Settlement_Period": np.int64, "Month":np.int64, "DRM_24h":np.float64, "DRM_8h":np.float64, "DRM_4h":np.float64, "DRM_2h":np.float64, "DRM_1h":np.float64, "Wind_Initial_Fcst":np.float64, "Wind_Latest_Fcst":np.float64, "Wind_Outturn":np.float64, "Solar_Fcst":np.float64, "NIV_Fcst":np.float64, "NIV":np.float64, "System_Price":np.float64, "APX_MIDP":np.float64, "System_Length":np.int64})

data_df = pd.read_excel("data.xlsx", index_col=0, parse_dates=["Datetime"])

print(data_df.info())

print(data_df.loc[date(2019,1,1)])

cols = []
cols = data_df.columns

categorical_cols = ["Settlement_Period", "Month", "System_Length"]
numerical_cols = []

for col in cols:
    if col not in categorical_cols:
        numerical_cols.append(col)
        
#print(data_df.isnull().sum())

desc_stats = data_df[numerical_cols].describe()

data_df = data_df.dropna(axis=0)

print(data_df.info())
print(data_df.System_Length.value_counts(normalize=True))

data_cleaned_df = data_df.drop(labels=["Wind_Outturn", "NIV", "System_Price", "APX_MIDP"], axis=1)

#data_cleaned_df[date(2019,1,1)].Month

params = {
        'objective' : 'binary',
        'metric' : 'auc',
        'learning_rate': 0.005,
        'num_leaves': 7,
        'max_bin': 240,
        'verbose': 0
        }

train_start = date(2017,1,1)
train_datetime = datetime(2018,12,31, 23, 30)

#test = data_cleaned_df[data_cleaned_df.Month==1].index
#print(data_cleaned_df.loc[test])

lgb_auc_score = {}
active_PnL = {}

flexible_volume = 10                        #in MWh

i=0
for i in range(22):
    train_date = train_datetime + timedelta(7*i)
    validation_date = train_datetime + timedelta(7*(i+1))
    
    print("------------------------------------------------------------------------------")
    print("Model training period is from {} to {}: ".format(train_start, train_date))
    print("Model validation period is from {} to {}: ".format(train_date + timedelta(minutes=30), validation_date))
    print("------------------------------------------------------------------------------")    
    
    #print(data_cleaned_df.loc[train_date])
    
    X_train = data_cleaned_df[:train_date].drop(labels=["System_Length"], axis=1)
    y_train = data_cleaned_df[:train_date].System_Length
    
    X_test = data_cleaned_df[train_date + timedelta(minutes=30):validation_date].drop(labels=["System_Length"], axis=1)
    y_test = data_cleaned_df[train_date + timedelta(minutes=30):validation_date].System_Length
    
    balancing_price = data_df[train_date + timedelta(minutes=30):validation_date].System_Price
    apx_price = data_df[train_date + timedelta(minutes=30):validation_date].APX_MIDP
    
    #create dataset for LightGBM
    lgb_train = lgb.Dataset(X_train, y_train)
    lgb_eval = lgb.Dataset(X_test, y_test, reference=lgb_train)
    
    
    
    evals_result = {}
    
    gbm  = lgb.train(params, lgb_train, num_boost_round=5000, early_stopping_rounds=200, 
                     categorical_feature=["Settlement_Period", "Month"], evals_result=evals_result,
                     valid_sets=[lgb_train, lgb_eval], valid_names=['train', 'eval'])
    
    
#    print('Plotting metrics recorded during training...')
#    ax = lgb.plot_metric(evals_result, metric='auc')
#    
#    print('Plotting feature importances...')
#    ax = lgb.plot_importance(gbm)
    
    y_pred_probs = gbm.predict(X_test, num_iteration=gbm.best_iteration)
    false_positive_rate, recall, thresholds = roc_curve(y_test, y_pred_probs)
    lgb_auc_score[(train_date + timedelta(minutes=30), train_datetime + timedelta(7*(i+1)))] = auc(false_positive_rate, recall)
    
    
    
    pnl1 = np.where(y_pred_probs > 0.65, flexible_volume*(balancing_price - apx_price), 0)
    pnl2 = np.where(y_pred_probs < 0.35, flexible_volume*(apx_price - balancing_price), 0)
    pnl = pnl1 + pnl2
    
    active_PnL[(train_date + timedelta(minutes=30), validation_date)] = pnl.sum()
    
Total_profit = 0

for k,v in active_PnL:
     Total_profit += active_PnL[(k,v)]

print("The total profit of the algo strategy is {}:".format(Total_profit))


