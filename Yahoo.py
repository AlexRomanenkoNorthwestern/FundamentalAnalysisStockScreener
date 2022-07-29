from audioop import avg
import Google
import General

# Import Libraries
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup, element
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta, date, time
from dateutil.relativedelta import relativedelta
    
def make_yahoo_request(ticker):
    yahoo_url = 'https://finance.yahoo.com/quote/' + ticker + '/analysis?p=' + ticker
    req = Request(url=yahoo_url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}) 
    response = urlopen(req)
    html = BeautifulSoup(response, features="lxml")
    return(html)

def get_algo_estimated_eps(ticker):

    return(3)

# Last 4 Quarters
# index zero is most recent
def get_historic_eps(html, ticker):
    # Read the contents of the file into 'html'
    stock_eps = html.find_all('tr')
    eps_list = []
    four_quarters_ago = stock_eps[15].find_all('td')[1].text
    eps_list.append(float(four_quarters_ago))
    three_quarters_ago = stock_eps[15].find_all('td')[2].text
    eps_list.append(float(three_quarters_ago))
    two_quarters_ago = stock_eps[15].find_all('td')[3].text
    eps_list.append(float(two_quarters_ago))
    one_quarter_ago = stock_eps[15].find_all('td')[4].text
    eps_list.append(float(one_quarter_ago))
    algo_estimate = get_algo_estimated_eps(ticker)
    eps_list.append(float(algo_estimate))
    return(eps_list)

# Next quarter Analyst EPS
def get_estimated_future_eps(html):
    # Read the contents of the file into 'html'
    stock_eps = html.find_all('tr')
    current_qtr = stock_eps[2].find_all('td')[1].text
    return(current_qtr)

# Last 4 Quarters
def get_historic_estimated_eps(html):
    # Read the contents of the file into 'html'
    stock_eps = html.find_all('tr')
    eps_list = []
    four_quarters_ago = stock_eps[14].find_all('td')[1].text
    eps_list.append(float(four_quarters_ago))
    three_quarters_ago = stock_eps[14].find_all('td')[2].text
    eps_list.append(float(three_quarters_ago))
    two_quarters_ago = stock_eps[14].find_all('td')[3].text
    eps_list.append(float(two_quarters_ago))
    one_quarter_ago = stock_eps[14].find_all('td')[4].text
    eps_list.append(float(one_quarter_ago))
    analyst_estimated = get_estimated_future_eps(html)
    eps_list.append(float(analyst_estimated))
    return(eps_list)

def get_earnings_date(ticker):
    date = General.get_finnhub_client().company_earnings(ticker)[0]["period"]
    return(date)

def update_bar_eps1(ticker):
    html = make_yahoo_request(ticker)

    one_quarter_ago = datetime.strptime(get_earnings_date(ticker), "%Y-%m-%d")
    two_quarters_ago = one_quarter_ago + relativedelta(months=-3)
    three_quarters_ago = one_quarter_ago + relativedelta(months=-6)
    four_quarters_ago = one_quarter_ago + relativedelta(months=-9)
    next_quarter = one_quarter_ago + relativedelta(months=3)
    x = [four_quarters_ago, three_quarters_ago, two_quarters_ago, one_quarter_ago, next_quarter,
         four_quarters_ago, three_quarters_ago, two_quarters_ago, one_quarter_ago, next_quarter]

    num_days =  (datetime.now()- (four_quarters_ago + relativedelta(months=-3))).days
    print(num_days)
    #x = ["One Year","Three Quarters","Two Quarters","Last Quarter","Next Quarter", 
         #"One Year","Three Quarters","Two Quarters","Last Quarter","Next Quarter"]
    
    y_historic = get_historic_eps(html, ticker)
    avg_eps = sum(y_historic[0:3])/4
    y_estimated = get_historic_estimated_eps(html)
    y_estimated.append(y_historic[0])
    y_estimated.append(y_historic[1])
    y_estimated.append(y_historic[2])
    y_estimated.append(y_historic[3])
    y_estimated.append(y_historic[4])
    type_eps = ["Expected", "Expected", "Expected", "Expected", "Expected", "Actual", "Actual", "Actual", "Actual", "Actual"]
    d1 = {"Time": x, "EPS": y_estimated, "Type": type_eps}
    df = pd.DataFrame(d1)
    fig = px.bar(df, x = "Time", y = "EPS", color = "Type", barmode = "group")

    # Google Line Chart
    date_list = [four_quarters_ago, three_quarters_ago, two_quarters_ago, one_quarter_ago, next_quarter]
    df_google = Google.google_trends_dataframe(ticker, num_days).iloc[:,0] * avg_eps/50
    print(df_google)

    avg_one_quarter_ago = df_google[(df_google.index <= one_quarter_ago) & (df_google.index > two_quarters_ago)].mean()
    avg_two_quarters_ago = df_google[(df_google.index <= two_quarters_ago) & (df_google.index > three_quarters_ago)].mean()
    avg_three_quarters_ago = df_google[(df_google.index <= three_quarters_ago) & (df_google.index > four_quarters_ago)].mean()
    avg_four_quarters_ago = df_google[(df_google.index <= four_quarters_ago) & (df_google.index > four_quarters_ago + relativedelta(months=-3))].mean()
    avg_next_quarter = df_google[(df_google.index <= next_quarter) & (df_google.index > one_quarter_ago)].mean()

    search_list = [avg_four_quarters_ago, avg_three_quarters_ago, avg_two_quarters_ago, avg_one_quarter_ago, avg_next_quarter]

    print(date_list)
    print(search_list)

    fig.add_trace(go.Scatter(x = date_list, y = search_list,
                    mode='lines+markers',
                    name='Google Trends'))
    #fig.add_trace(
       # go.Scatter(name = "Google Trends", x = ["One Year","Three Quarters","Two Quarters","Last Quarter","Next Quarter"], y = [1,1.5,1.25,2, 3])
        #)
    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color = 'white')
    fig.update_yaxes(title = "EPS")
    fig.update_xaxes(tickangle = 0)
    return(fig)
