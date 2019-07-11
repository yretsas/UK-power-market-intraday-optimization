# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 19:22:07 2019

@author: yiannisPC
"""

import pandas as pd
import numpy as np
import requests as r
from datetime import datetime, date, timedelta
import io

scripting_key = "hcpzy6pdp7pttpr"

year = 2016

settlement_date = date(year, 1, 1)

url = "https://api.bmreports.com/BMRS/B1770/v1?APIKey=" + scripting_key + "&SettlementDate=" + settlement_date.isoformat() + "&Period=*"  + "&ServiceType=csv"

res = r.get(url)
print(res.status_code)
url_data = res.content

#print(url_data)

raw_data = pd.read_csv(io.StringIO(url_data.decode()), index_col=False, skiprows=5, skipfooter=1, engine='python',
                                       names=["Doc_ID", "Doc_RevNum", "Active_Flag", "Process_Type", "Doc_type", "Resolution", "Curve_Type",  "Price_Cat", "Imbal_Price", "Settlement_Period", "Settlement_Date", "Control_Area", "TimeSeries_ID", "Doc_status"],
                                       parse_dates=["Settlement_Date" ])


