# UK-power-market-intraday-optimization

This is an example of an intraday optimization algo for the UK Power market for a market participant that has some volume flexibility. 

Publicly available information is being used from the National Grid API to structure the data-set for the progressive out-of-sample validation. 

The active strategy is determined by forecasting system length per settlement period (intraday) and positioning on the spread between intraday spot prices and balancing prices. 

The scripts contain the data collection process from the NG api and the analysis.py has the progressive out-of-sample validation of the strategy. The neural_test.py has a neural net implementation of the strategy using Keras sequential model and LSTM layers. It is not optimally tuned yet but it still manages to make some profit out of sample. 

This is a basic implementation and it can be vastly improved with the use of more system information and proprietory data. 

List of things to follow (not necessarily in the order below): 
1. Some more feature engineering to boost performance. 
2. Link to detailed weather information 
3. Create a data pipeline for a realistic trading set-up
