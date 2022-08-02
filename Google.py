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
import numpy as np


# Returns a dataframe for google search trends of a given search term over a period of time
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

  
# Displays a google search trends graph
def google_trends_graph(dataframe):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dataframe.index, y = dataframe.iloc[:,0],
                    mode='lines+markers',
                    name='Google Search Volume'))
    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color = 'white')
    fig.update_yaxes(title = "Search Volume")
    fig.update_xaxes(title = "Date")
    fig.update_xaxes(tickangle = 0)
    fig.update_xaxes(showgrid = False)
    fig.update_layout(title = {
        'text': "Google Trends Searches",
        'xanchor': 'center',
        'x': 0.5})
    return(fig)

    
# Returns relative google trends search volume for a search term
# Compares the most recent 1/4 of a period to the other 3/4 of the period
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
