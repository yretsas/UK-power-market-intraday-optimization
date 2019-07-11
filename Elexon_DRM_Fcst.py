# -*- coding: utf-8 -*-
"""
Created on Sat Jun 29 14:48:00 2019

@author: yiannisPC
"""

import pandas as pd
import numpy as np
import requests as r
from datetime import datetime, date, timedelta
import io

scripting_key = "hcpzy6pdp7pttpr"

DRM_Fcst_df = pd.DataFrame(columns=["Settlement_Date", "Settlement_Period", "DRM_24h", "DRM_8h", "DRM_4h", "DRM_2h", "DRM_1h"])

year = 2018

for i in range(365):

    settlement_date = date(year, 1, 1) + timedelta(i)
    
    url = "https://api.bmreports.com/BMRS/LOLPDRM/v1?APIKey=" + scripting_key + "&FromSettlementDate=" + settlement_date.isoformat() + "&&ToSettlementDate=" + settlement_date.isoformat() + "&ServiceType=csv"
    
    res = r.get(url)
    print(res.status_code)
    
    url_data = res.content
    
    raw_data = pd.read_csv(io.StringIO(url_data.decode()), skiprows=1, skipfooter=1, engine='python',
                                       names=["Record_Type", "Settlement_Date", "Settlement_Period", "LOLP_24h", "DRM_24h", "LOLP_8h", "DRM_8h", "LOLP_4h", "DRM_4h", "LOLP_2h", "DRM_2h", "LOLP_1h", "DRM_1h", "Active_Flag"],
                                       parse_dates=["Settlement_Date", ])
    
    cleaned_data = raw_data.drop(labels=["Record_Type", "LOLP_24h", "LOLP_8h", "LOLP_4h", "LOLP_2h", "LOLP_1h", "Active_Flag"], axis=1)

    DRM_Fcst_df = DRM_Fcst_df.append(cleaned_data, ignore_index=True)
    
DRM_Fcst_df.to_csv("DRM_Fcst_" + str(year) + ".csv")

