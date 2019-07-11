# -*- coding: utf-8 -*-
"""
Created on Sat Jun 29 13:29:35 2019

@author: yiannisPC
"""

import pandas as pd
import numpy as np
import requests as r
from datetime import datetime, date, timedelta
import io

scripting_key = "hcpzy6pdp7pttpr"

Wind_Fcst_df = pd.DataFrame(columns=["Record_Type", "Settlement_Date", "Settlement_Period", "Initial_Fcst", "Latest_Fcst", "Outturn"])

year = 2019

for i in range(160):

    settlement_date = date(year, 1, 1) + timedelta(i)
    
    url = "https://api.bmreports.com/BMRS/WINDFORFUELHH/v1?APIKey=" + scripting_key + "&FromDate=" + settlement_date.isoformat() + "&ToDate=" + settlement_date.isoformat() + "&ServiceType=csv"
    
    res = r.get(url)
    print(res.status_code)
    
    url_data = res.content
    
    raw_data = pd.read_csv(io.StringIO(url_data.decode()), skiprows=1, skipfooter=1, engine='python',
                                   names=["Record_Type", "Settlement_Date", "Settlement_Period", "Initial_Fcst_time", "Initial_Fcst", "Latest_Fcst_time", "Latest_Fcst", "Outturn_time", "Outturn", "Active_Flag"],
                                   parse_dates=["Settlement_Date", "Initial_Fcst_time", "Latest_Fcst_time", "Outturn_time"])
    
    cleaned_data = raw_data.drop(labels=["Initial_Fcst_time", "Latest_Fcst_time", "Outturn_time", "Active_Flag"], axis=1)
    
#    print(cleaned_data.isnull().sum())
    
    null_index = cleaned_data.index[cleaned_data.Initial_Fcst.isnull()].tolist()
    
    for i in null_index:
        cleaned_data.loc[i,"Initial_Fcst"] = cleaned_data.loc[i-1,"Initial_Fcst"]
        cleaned_data.loc[i,"Latest_Fcst"] = cleaned_data.loc[i-1,"Latest_Fcst"]
    
    Wind_Fcst_df = Wind_Fcst_df.append(cleaned_data, ignore_index=True)
    
Wind_Fcst_df.to_csv("Wind_Fcst_Outturn_" + str(year) + ".csv")
