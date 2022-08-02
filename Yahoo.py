import Google
import General
import EarningsAlgo

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
import statistics

# Returns the html for a ticker's yahoo finannce analysis webpage
def make_yahoo_request(ticker):
    yahoo_url = 'https://finance.yahoo.com/quote/' + ticker + '/analysis?p=' + ticker
    req = Request(url=yahoo_url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}) 
    response = urlopen(req)
    html = BeautifulSoup(response, features="lxml")
    return(html)


# Returns the estimated_eps for next quarter using our algorithim
def get_algo_estimated_eps(ticker):
    estimate = EarningsAlgo.get_algo_eps_projection(ticker)
    return(estimate)


# Returns the past four quarters eps in addition to next quarter's projected eps
def get_historic_eps(html, ticker):
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


# Returns next quarter's projected EPS from analysts 
def get_estimated_future_eps(html):
    stock_eps = html.find_all('tr')
    current_qtr = stock_eps[2].find_all('td')[1].text
    return(current_qtr)


# Returns analysts' projections for the  past four quarters eps in addition to next quarter's projected eps
def get_historic_estimated_eps(html):
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


# Returns a bar chart with historical estimated and actual eps, as well as an eps projection
def update_bar_eps(ticker):
    html = make_yahoo_request(ticker)
    one_quarter_ago = datetime.strptime(General.get_earnings_date(ticker), "%Y-%m-%d")
    two_quarters_ago = one_quarter_ago + relativedelta(months=-3)
    three_quarters_ago = one_quarter_ago + relativedelta(months=-6)
    four_quarters_ago = one_quarter_ago + relativedelta(months=-9)
    next_quarter = one_quarter_ago + relativedelta(months=3)
    x = [four_quarters_ago, three_quarters_ago, two_quarters_ago, one_quarter_ago, next_quarter,
         four_quarters_ago, three_quarters_ago, two_quarters_ago, one_quarter_ago, next_quarter]

    num_days =  (datetime.now()- (four_quarters_ago + relativedelta(months=-3))).days
   
    y_historic = get_historic_eps(html, ticker)
    avg_eps = sum(y_historic[0:4])/4
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
    google_data = Google.google_trends_dataframe(ticker, num_days).iloc[:,0]
    df_google = google_data * avg_eps/google_data[(google_data.index <= one_quarter_ago) & (google_data.index > four_quarters_ago + relativedelta(months=-3))].mean()

    avg_one_quarter_ago = df_google[(df_google.index <= one_quarter_ago) & (df_google.index > two_quarters_ago)].mean()
    avg_two_quarters_ago = df_google[(df_google.index <= two_quarters_ago) & (df_google.index > three_quarters_ago)].mean()
    avg_three_quarters_ago = df_google[(df_google.index <= three_quarters_ago) & (df_google.index > four_quarters_ago)].mean()
    avg_four_quarters_ago = df_google[(df_google.index <= four_quarters_ago) & (df_google.index > four_quarters_ago + relativedelta(months=-3))].mean()
    avg_next_quarter = df_google[(df_google.index <= next_quarter) & (df_google.index > one_quarter_ago)].mean()

    search_list = [avg_four_quarters_ago, avg_three_quarters_ago, avg_two_quarters_ago, avg_one_quarter_ago, avg_next_quarter]

    fig.add_trace(go.Scatter(x = date_list, y = search_list,
                    mode='lines+markers',
                    name='Google Trends'))

    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color = 'white')
    fig.update_yaxes(title = "EPS")
    fig.update_xaxes(tickangle = 0)
    fig.update_layout(title = {
        'text': "Historic EPS and Projection",
        'xanchor': 'center',
        'x': 0.5})
    return([fig, search_list[0:4], y_historic[0:4]])


# Displays a candlestick chart for stocks with a "fair value" price target with a 95% confidence interval
def update_stk_chart(ticker):
    stk_df = yf.Ticker(ticker).history(period ="2y", actions = False)
    fig_stk = go.Figure(data=[go.Candlestick(x=stk_df.index,
                                             open = stk_df['Open'],
                                             high = stk_df['High'],
                                             low = stk_df['Low'],
                                             close = stk_df['Close'])])

    value = EarningsAlgo.get_company_health(ticker)
    x_line = [value[0][len(value[0])-1], value[2]]
    y_line = [value[4],50/value[3]*stk_df['Close'][len(stk_df['Close'])-1]]
    fig_stk.add_trace(go.Scatter(x=x_line, y = y_line,
                    mode='lines+markers',
                    name = "Projection"))
    
    results = update_bar_eps(ticker)

    #Google Projected EPS
    projection_eps = results[1]

    #Reported EPS
    actual_eps = results[2]

    adj_eps = 50/value[3]
    new_eps = [actual_eps[0]/projection_eps[0]*adj_eps,
                  actual_eps[1]/projection_eps[1]*adj_eps,
                  actual_eps[2]/projection_eps[2]*adj_eps,
                  actual_eps[3]/projection_eps[3]*adj_eps]

    # 95% Confidence Interval of Price
    std_dev = statistics.pstdev(new_eps)
    CI = [(adj_eps -1.96*std_dev/2)*stk_df['Close'][len(stk_df['Close'])-1], (adj_eps + 1.96*std_dev/2)*stk_df['Close'][len(stk_df['Close'])-1]]

    # Add in Upper Bound Line
    fig_stk.add_trace(go.Scatter(x=x_line, y = [value[4], CI[0]],
                    mode='lines+markers',
                    name='Lower',))

    # Add in Lower Bound Line
    fig_stk.add_trace(go.Scatter(x=x_line, y = [value[4], CI[1]],
                    mode='lines+markers',
                    name='Upper'))
    fig_stk.update_layout(margin=dict(l=20, r=20, t=30, b=20),
                          paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)',
                          font_color = 'white')

    fig_stk.update_layout(title = {
        'text': "Stock Price and Projection",
        'xanchor': 'center',
        'x': 0.5})

    return(fig_stk)
