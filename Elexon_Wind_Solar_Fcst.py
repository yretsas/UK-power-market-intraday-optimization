# -*- coding: utf-8 -*-
"""
Created on Sat Jun 29 11:41:05 2019

Use the Elexon APi to get NGs Day-ahead Wind & Solar generation forecast data. 

That can serve as part of a data pipeline  in a forecasting platform.

@author: yiannisPC
"""
import pandas as pd
import requests as r
from datetime import datetime, date, timedelta
import io

scripting_key = "hcpzy6pdp7pttpr"

Solar_Fcst_df = pd.DataFrame(columns=["Resource Type", "Setllement_Date", "Process_Type", "Setllement_Period", "Quantity"])
WindOnshore_Fcst_df = pd.DataFrame(columns=["Resource Type", "Setllement_Date", "Process_Type", "Setllement_Period", "Quantity"])
WindOffshore_Fcst_df = pd.DataFrame(columns=["Resource Type", "Setllement_Date", "Process_Type", "Setllement_Period", "Quantity"])


year = 2019

for i in range(160):
    
    settlement_date = date(year, 1, 1) + timedelta(i)
    
    url = "https://api.bmreports.com/BMRS/B1440/v1?APIKey=" + scripting_key + "&SettlementDate=" + settlement_date.isoformat() + "&Period=*&ServiceType=csv"
    
    res = r.get(url)
    print(res.status_code)
    
    url_data = res.content
    
    #print(url_data.decode())
    
    raw_data = pd.read_csv(io.StringIO(url_data.decode()), engine='python', skiprows=5, skipfooter=1,
                               names=["Time_Series_ID", "Business_Type", "Resource Type", "Setllement_Date", "Process_Type", "Setllement_Period", "Quantity", "Doc_Type", "Curve_Type", "Resolution", "Active_Flag", "Doc_ID", "Doc_RevNum"],
                               parse_dates=["Setllement_Date"])
    
    cleaned_data = raw_data.drop(labels=["Time_Series_ID", "Business_Type", "Doc_Type", "Curve_Type", "Resolution", "Active_Flag", "Doc_ID", "Doc_RevNum"], axis=1)
    
    solar = cleaned_data[(cleaned_data["Resource Type"] == "Solar") & ((cleaned_data["Process_Type"] =="Day Ahead") | (cleaned_data["Process_Type"] =="Day ahead"))].sort_values(by=["Setllement_Period"], ascending=True)
    wind_onshore = cleaned_data[(cleaned_data["Resource Type"] == "Wind Onshore") & ((cleaned_data["Process_Type"] =="Day Ahead") | (cleaned_data["Process_Type"] =="Day ahead"))].sort_values(by=["Setllement_Period"], ascending=True)
    wind_offshore = cleaned_data[(cleaned_data["Resource Type"] == "Wind Offshore") & ((cleaned_data["Process_Type"] =="Day Ahead") | (cleaned_data["Process_Type"] =="Day ahead"))].sort_values(by=["Setllement_Period"], ascending=True)
    
    Solar_Fcst_df = Solar_Fcst_df.append(solar, ignore_index=True)
    WindOnshore_Fcst_df = WindOnshore_Fcst_df.append(wind_onshore, ignore_index=True)
    WindOffshore_Fcst_df = WindOffshore_Fcst_df.append(wind_offshore, ignore_index=True)
    
Solar_Fcst_df.to_csv("Solar_Fcst_" + str(year) + ".csv")
WindOnshore_Fcst_df.to_csv("WindOnshore_Fcst_" + str(year) + ".csv")
WindOffshore_Fcst_df.to_csv("WindOffshore_Fcst_" + str(year) + ".csv")

