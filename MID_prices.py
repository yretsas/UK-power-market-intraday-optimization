# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 20:00:13 2019

@author: yiannisPC
"""

import pandas as pd
import numpy as np
import requests as r
from datetime import datetime, date, timedelta
import io

scripting_key = "hcpzy6pdp7pttpr"

APXMIDP_df = pd.DataFrame(columns=["Data_Provider", "Settlement_Date", "Settlement_Period", "Price", "Volume"])

year = 2019

for i in range(160):

    settlement_date = date(year, 1, 1) + timedelta(i)
    
    url = "https://api.bmreports.com/BMRS/MID/v1?APIKey=" + scripting_key + "&FromSettlementDate=" + settlement_date.isoformat() + "&ToSettlementDate=" + settlement_date.isoformat()  + "&Period=*&ServiceType=csv"
    
    res = r.get(url)
    print(res.status_code)
    url_data = res.content
    
    raw_data = pd.read_csv(io.StringIO(url_data.decode()), index_col=False, skiprows=1, skipfooter=1, engine='python',
                                           names=["Record_Type", "Data_Provider", "Settlement_Date", "Settlement_Period", "Price", "Volume", "Active_Flag"],
                                           parse_dates=["Settlement_Date" ])
    
    cleaned_data = raw_data[raw_data["Data_Provider"] == "APXMIDP"].drop(labels=["Record_Type", "Active_Flag"], axis=1)

    APXMIDP_df = APXMIDP_df.append(cleaned_data, ignore_index=True)
    
APXMIDP_df.to_csv("APX_MIDP_" + str(year) + "_.csv")