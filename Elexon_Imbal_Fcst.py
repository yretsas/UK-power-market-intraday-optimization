# -*- coding: utf-8 -*-
"""
Created on Sat Jun 29 10:22:22 2019

Use the Elexon APi to get NGs NIV volume forecast data. 

That can serve as part of a data pipeline  in a forecasting platform.

@author: yiannisPC
"""

import pandas as pd
import requests as r
from datetime import datetime, date, timedelta
import io

scripting_key = "hcpzy6pdp7pttpr"

Imbal_Fcst_df = pd.DataFrame(columns=["Zone ID", "Settlement Date", "Settlement Period", "Record Type", "Publish Time", "Imbal Fcst"])

year = 2019

for i in range(160):

    date_from_to = date(year,1,1) + timedelta(i)
    
    url = "https://api.bmreports.com/BMRS/MELIMBALNGC/v1?APIKey=" + scripting_key +"&FromDate=" + date_from_to.isoformat() + "&ToDate=" + date_from_to.isoformat() + "&ServiceType=csv"
    
    res = r.get(url)
    print(res.status_code)
    
    url_data = res.content
    
    raw_data = pd.read_csv(io.StringIO(url_data.decode()), skiprows=1, skipfooter=1,
                           names=["Zone ID", "Settlement Date", "Settlement Period", "Record Type", "Publish Time", "Imbal Fcst"],
                           parse_dates=["Settlement Date", "Publish Time"])
    
    clean_data = raw_data[raw_data["Zone ID"] == "DAI"]
    
    
    Imbal_Fcst_df = Imbal_Fcst_df.append(clean_data, ignore_index=True)
    
Imbal_Fcst_df.to_csv("Imbal_Fcst_" + str(year) + ".csv")