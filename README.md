# UK-power-market-intraday-optimization

This is an example of an intraday optimization algo for the UK Power market for a market participant that has some volume flexibility. 

Publicly available information is being used from the National Grid API to structure the data-set for the progressive out-of-sample validation. 

The active strategy is determined my forecasting system length per settlement period (intraday) and positioning on the spread between intraday spot prices and balancing prices. 

The scripts contain the data collection process from the NG api and the analysis.py has the progressive out-of-sample validation of the strategy. 

This is a basic implementation and it can be vastly improved with the use of more system information and proprietory data. 
