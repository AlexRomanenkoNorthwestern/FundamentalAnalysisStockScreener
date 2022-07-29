import General

# Import Libraries
import pandas as pd
import pytrends
from pytrends.request import TrendReq
from pytrends import dailydata
pytrends = TrendReq()
from datetime import datetime, timedelta, date, time
import plotly.graph_objects as go
import math


# Returns a Dataframe for google search trends of a given search term over a period of time
# Example Usage: google_trends_dataframe('CROX', 180)
# For Daily Data: Total_days must be between 30 and 180
def google_trends_dataframe(ticker, total_days):

    search_term = General.get_brand_name(ticker)
    start_date = (datetime.today() - timedelta(days=total_days - 1)).strftime("%Y-%m-%d")
    end_date = datetime.today().strftime("%Y-%m-%d")
    kw_list = [search_term]
    pytrends.build_payload(kw_list, cat=0, timeframe='{} {}'.format(start_date, end_date), geo='', gprop='')
    interest = pytrends.interest_over_time()
    if(interest.empty):
        kw_list = [ticker]
        pytrends.build_payload(kw_list, cat=0, timeframe='{} {}'.format(start_date, end_date), geo='', gprop='')
        interest = pytrends.interest_over_time()
    return interest

  
# Displays a Google Search Trends Graph
def google_trends_graph(dataframe):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=np.linspace(1,len(dataframe)), y = dataframe.iloc[:,0],
                    mode='lines+markers',
                    name='lines+markers'))
    fig.show()

    
# Returns Relative Google Trends Search Volume for a Search Term
# Compares the most recent 1/4 of a period to the other 3/4 of the period
# Returns a value from -100% to infinityt%
def relative_search_volume_google (dataframe,total_days):
    if (len(dataframe) < total_days):
        total_days = len(dataframe)
    first_three_fourths = math.floor(total_days*.75) - 1
    average_three_fourths = dataframe.iloc[1:first_three_fourths, 0].mean()
    average_current_quarter = dataframe.iloc[first_three_fourths:total_days, 0].mean()
    result = (average_current_quarter*100/average_three_fourths)-100
    if (result > 0):
        return ("+{}%".format(int(result)))
    else:
        return("{}%".format(int(result)))
