# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 22:03:28 2019

@author: yiannisPC
"""

import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from sklearn.metrics import mean_squared_error, mean_absolute_error, roc_curve, roc_auc_score, auc
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

from keras import backend as K
print(K.tensorflow_backend._get_available_gpus())

import tensorflow as tf
import keras
from keras.regularizers import l1, l2
from keras import losses
from keras.optimizers import Adam, Nadam
from keras.layers import Dense, LSTM, Dropout
from keras.models import Sequential
from keras.callbacks import EarlyStopping

K.clear_session()

data_df = pd.read_excel("data.xlsx", index_col=0, parse_dates=["Datetime"])

#print(data_df.info())

cols = []
cols = data_df.columns

categorical_cols = ["Settlement_Period", "Month", "System_Length"]
numerical_cols = []

for col in cols:
    if col not in categorical_cols:
        numerical_cols.append(col)
        
desc_stats = data_df[numerical_cols].describe()

data_df = data_df.dropna(axis=0)

#print(data_df.info())
print(data_df.System_Length.value_counts(normalize=True))

data_cleaned_df = data_df.drop(labels=["Wind_Outturn", "NIV", "System_Price", "APX_MIDP"], axis=1)

data_cleaned_df.drop(labels=["Settlement_Period", "Month"], axis=1, inplace=True)

#scale the data for the neural net
main_scaler = MinMaxScaler(feature_range=(-1,1))

data_scaled  = main_scaler.fit_transform(data_cleaned_df.drop(labels=["System_Length"], axis=1))

columns = []
for col in data_cleaned_df.columns:
    if col != "System_Length":
        columns.append(col)

#put scaled data in a dataframe
data_scaled_df = pd.DataFrame(data_scaled, index=data_cleaned_df.index, columns=columns)


def model_fit(data_df, X_train, y_train, X_test, y_test, optimizer, batch=16):
    graph = tf.Graph()
    K.clear_session()
    
    with tf.Session(graph=graph):
        model = Sequential()
        model.add(LSTM(100, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
        model.add(Dropout(0.1))
        model.add(LSTM(40, return_sequences=True, kernel_regularizer=l2(0.0001), recurrent_regularizer=l2(0.0001)))
        model.add(Dropout(0.1))
        model.add(LSTM(10))
        model.add(Dropout(0.1))
        model.add(Dense(1))
        
        model.compile(loss=losses.binary_crossentropy, optimizer=optimizer, metrics=[keras.metrics.binary_accuracy])
        
        early_stopper = EarlyStopping(monitor='val_loss', patience=8, restore_best_weights=True)
        model.fit(X_train, y_train, epochs=200, batch_size=batch, validation_data=(X_test, y_test), callbacks=[early_stopper], verbose=1, shuffle=False)
        
        y_pred_probs = model.predict(X_test)
        false_positive_rate, recall, thresholds = roc_curve(y_test, y_pred_probs)
        auc_score = auc(false_positive_rate, recall)
        
        balancing_price = data_df[validation_start:validation_end].System_Price
        apx_price = data_df[validation_start:validation_end].APX_MIDP
        
        y_pred_probs = y_pred_probs.reshape(y_pred_probs.shape[0],)
        pnl1 = np.where(y_pred_probs > 0.65, flexible_volume*(balancing_price - apx_price), 0)
        pnl2 = np.where(y_pred_probs < 0.35, flexible_volume*(apx_price - balancing_price), 0)
        pnl = pnl1 + pnl2
    
    K.clear_session()
    
    return auc_score, pnl1, pnl2, pnl, y_pred_probs
    

lstm_auc_score = {}
active_PnL = {}

flexible_volume = 10                        #in MWh

#set the initial training window
train_start = date(2017,1,1)
train_stop = datetime(2018,12,24, 23, 30)

i=0
for i in range(22):
    train_start = train_start + timedelta(7)    
    train_stop = train_stop + timedelta(7)
    validation_start = train_stop + timedelta(minutes=30)
    validation_end = validation_start + timedelta(7)
    
    print("------------------------------------------------------------------------------")
    print("Model training period is from {} to {}: ".format(train_start, train_stop))
    print("Model validation period is from {} to {}: ".format(validation_start, validation_end))
    print("------------------------------------------------------------------------------")  
    
    X_train_df = data_scaled_df[train_start:train_stop]
    y_train_df = data_cleaned_df[train_start:train_stop].System_Length
    
    X_test_df = data_scaled_df[validation_start:validation_end]
    y_test_df = data_cleaned_df[validation_start:validation_end].System_Length
    
    X_train = X_train_df.values
    y_train = y_train_df.values
    X_test = X_test_df.values
    y_test = y_test_df.values
    
    'Reshape input to 3D for LSTM neural net'
    X_train = X_train.reshape((X_train.shape[0], 1, X_train.shape[1]))
    X_test = X_test.reshape((X_test.shape[0], 1, X_test.shape[1]))
        
    auc_score, pnl, pnl1, pnl2, y_pred_probs = model_fit(data_df, X_train, y_train, X_test, y_test, "adam", 12)
    lstm_auc_score[(validation_start, validation_end)] = auc_score
    active_PnL[(validation_start, validation_end)] = pnl.sum()
    
Total_profit = 0

for k,v in active_PnL:
     Total_profit += active_PnL[(k,v)]

print("The total profit of the algo strategy is {}:".format(Total_profit))

