from pandas_datareader import data as pdr
import datetime as dt
import pandas as pd
import pytrends
from pytrends.request import TrendReq
pytrends = TrendReq()
from datetime import datetime, timedelta
import math
import plotly.graph_objects as go
import finnhub

# API Keys
finnhub_client = finnhub.Client(api_key="INSERT_API_KEY")

# Retrieves a stock ticker's company name and removes business types such as LLC, Ltd, Inc
# Example Usage: get_brand_name('CROX')
def get_brand_name (ticker):
  try:
    company_name = finnhub_client.company_profile2(symbol= ticker)['name'].split(' ')
  except:
    print('Stock ticker not found')
  company_name = company_name[0:len(company_name)-1]
  company_name = ' '.join(company_name)
  return(company_name)


# Returns a Dataframe for google search trends of a given search term over a period of time
# Example Usage: google_trends_dataframe('CROX', 180)
# For Daily Data: Total_days must be between 30 and 180
def google_trends_dataframe(ticker, total_days):
    search_term = get_brand_name(ticker)
    start_date = (datetime.today() - timedelta(days=total_days - 1)).strftime("%Y-%m-%d")
    end_date = datetime.today().strftime("%Y-%m-%d")
    kw_list = [search_term]
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
def relative_search_volume (dataframe,total_days):
    if (len(dataframe) < total_days):
        total_days = len(dataframe)
    
    first_three_fourths = math.floor(total_days*.75) - 1
    average_three_fourths = dataframe.iloc[1:first_three_fourths, 0].mean()
    average_current_quarter = dataframe.iloc[first_three_fourths:total_days, 0].mean()
    return ((average_current_quarter*100/average_three_fourths)-100)
