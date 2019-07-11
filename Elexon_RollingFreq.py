# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 20:26:56 2019

@author: yiannisPC
"""

import pandas as pd
import numpy as np
import requests as r
from datetime import datetime, date, timedelta
import io

scripting_key = "hcpzy6pdp7pttpr"

year = 2016

settlement_date = datetime(year, 1, 1) + timedelta(minutes=30)

url = "https://api.bmreports.com/BMRS/FREQ/v1?APIKey=" + scripting_key + "&SettlementDate=" + settlement_date.isoformat() + "&Period=*"  + "&ServiceType=csv"

res = r.get(url)
print(res.status_code)
url_data = res.content