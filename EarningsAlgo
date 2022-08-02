import Google
import General


import pandas as pd
import datetime as dt
from datetime import datetime, timedelta, date, time
import numpy as np
import math
from dateutil.relativedelta import relativedelta
import finnhub
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup, element
from sklearn import linear_model
from sklearn.model_selection import  train_test_split
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go

# Returns the html for a ticker's yahoo finannce analysis webpage
def make_yahoo_request(ticker):
    yahoo_url = 'https://finance.yahoo.com/quote/' + ticker + '/analysis?p=' + ticker
    req = Request(url=yahoo_url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}) 
    response = urlopen(req)
    html = BeautifulSoup(response, features="lxml")
    return(html)


# Returns the past four quarters eps 
def get_historic_eps(html):
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
    return(eps_list)


# Returns next quarter's projected EPS from analysts 
def get_estimated_future_eps(html):
    # Read the contents of the file into 'html'
    stock_eps = html.find_all('tr')
    current_qtr = stock_eps[2].find_all('td')[1].text
    return(current_qtr)


# Returns analysts' projections for the  past four quarters eps in addition to next quarter's projected eps
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


# Weighted Correlation Calculation****************************************

# Weights sum to 1
def weights (length):
    most_recent_weighting = .1
    weight_factor = .9
    vector = []
    for i in range(1,length+1):
        vector.append(most_recent_weighting)
        most_recent_weighting *= weight_factor
    total = sum(vector)
    array = np.array(vector)
    vector = array * 1/total #vector weights sum to 1
    return(vector)

# Weighted Mean
def m(x,w):
    total = 0
    x = np.array(x)
    for i in np.linspace(0,len(x)-1, num = len(x)):
        total += x[int(i)] * w[int(i)]
    return(total/np.sum(w))

# Weighted Covariance
def cov(x,y,w):
    total = 0
    x = np.array(x)
    y = np.array(y)
    for i in np.linspace(0,len(x)-1, num = len(x)):
        total += w[int(i)] * (x[int(i)] - m(x,w)) * (y[int(i)]- m(y,w))
    return(total/np.sum(w))

# Weighted Correlation
def weighted_corr(x,y,w):
    return(cov(x,y,w)/np.sqrt(cov(x,x,w)*cov(y,y,w)))


# Correlation between earnings estimates and historic eps
def correlation_estimates(ticker, historic_actual_eps):
    yahoo_request = make_yahoo_request(ticker)
    historic_estimated_eps = get_historic_estimated_eps(yahoo_request)[0:4]
    correlation = weighted_corr(historic_actual_eps, historic_estimated_eps, weights(4))
    return abs(correlation)


# Correlation between google trends and historic eps
def correlation_google_trends(ticker, historic_actual_eps):
    search_term = General.get_brand_name(ticker)

    # Get Earnings data list
    avg_eps = sum(historic_actual_eps)/4

    # Get Search Trends data
    one_quarter_ago = datetime.strptime(General.get_earnings_date(ticker), "%Y-%m-%d")
    two_quarters_ago = one_quarter_ago + relativedelta(months=-3)
    three_quarters_ago = one_quarter_ago + relativedelta(months=-6)
    four_quarters_ago = one_quarter_ago + relativedelta(months=-9)
    num_days =  (datetime.now()- (four_quarters_ago + relativedelta(months=-3))).days
    df_google = Google.google_trends_dataframe(search_term, num_days).iloc[:,0] * avg_eps/50
    avg_one_quarter_ago = df_google[(df_google.index <= one_quarter_ago) & (df_google.index > two_quarters_ago)].mean()
    avg_two_quarters_ago = df_google[(df_google.index <= two_quarters_ago) & (df_google.index > three_quarters_ago)].mean()
    avg_three_quarters_ago = df_google[(df_google.index <= three_quarters_ago) & (df_google.index > four_quarters_ago)].mean()
    avg_four_quarters_ago = df_google[(df_google.index <= four_quarters_ago) & (df_google.index > four_quarters_ago + relativedelta(months=-3))].mean()
    search_list = [avg_four_quarters_ago, avg_three_quarters_ago, avg_two_quarters_ago, avg_one_quarter_ago]
    correlation = weighted_corr(historic_actual_eps, search_list, weights(4))
    return abs(correlation)


# Projected eps based on google trends 
def projection_google(ticker, historic_actual_eps):
    one_quarter_ago = datetime.strptime(General.get_earnings_date(ticker), "%Y-%m-%d")
    four_quarters_ago = one_quarter_ago + relativedelta(months=-9)
    next_quarter = one_quarter_ago + relativedelta(months=3)
    num_days =  (datetime.now()- (four_quarters_ago + relativedelta(months=-3))).days
    avg_eps = sum(historic_actual_eps[0:4])/4
    google_data = Google.google_trends_dataframe(ticker, num_days).iloc[:,0]
    df_google = google_data * avg_eps/google_data[(google_data.index <= one_quarter_ago) & (google_data.index > four_quarters_ago + relativedelta(months=-3))].mean()
    projection = df_google[(df_google.index <= next_quarter) & (df_google.index > one_quarter_ago)].mean()
    return abs(projection)


# Finds insider data for the past four quarters and next quarter
def get_insider_data(ticker):
    finnhub_client = General.get_finnhub_client()
    one_quarter_ago = datetime.strptime(finnhub_client.company_earnings(ticker)[0]["period"], "%Y-%m-%d")
    two_quarters_ago = one_quarter_ago + relativedelta(months=-3)
    three_quarters_ago = one_quarter_ago + relativedelta(months=-6)
    four_quarters_ago = one_quarter_ago + relativedelta(months=-9)
    next_quarter = one_quarter_ago + relativedelta(months=3)

    insider_next_q = finnhub_client.stock_insider_transactions(ticker, one_quarter_ago, next_quarter)["data"]
    insider_one_q_ago = finnhub_client.stock_insider_transactions(ticker, two_quarters_ago, one_quarter_ago)["data"]
    insider_two_q_ago = finnhub_client.stock_insider_transactions(ticker, three_quarters_ago, two_quarters_ago)["data"]
    insider_three_q_ago = finnhub_client.stock_insider_transactions(ticker, four_quarters_ago, three_quarters_ago)["data"]
    insider_four_q_ago = finnhub_client.stock_insider_transactions(ticker, four_quarters_ago + relativedelta(months=-3), four_quarters_ago)["data"]
    data_list = [insider_next_q, insider_one_q_ago, insider_two_q_ago, insider_three_q_ago, insider_four_q_ago]
    change_shares_list = []
    total = 0
    for i in data_list:
        total = 0
        for j in i:
            total += int(j["change"])
        change_shares_list.append(total)
    return(change_shares_list)


# Correlation between insider transactions and historic eps
def correlation_insider(ticker, historic_actual_eps):
    data_list = get_insider_data(ticker)[0:4]
    correlation = weighted_corr(historic_actual_eps, data_list, weights(4))
    #Checks to make sure nan is not returned from the correlation calculation
    try:
        correlation = float(correlation)
    except:
        return(0)
    return abs(correlation/4)


# Projected EPS based on insider transactions
def projection_insider(ticker, historic_actual_eps):
    data_list = get_insider_data(ticker)
    reg = linear_model.LinearRegression()
    x = np.array(data_list[0:4]).reshape(-1,1)
    y = np.array(historic_actual_eps).reshape(-1,1)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.25)
    reg.fit(x_train, y_train)
    return((reg.intercept_ + reg.coef_*data_list[4])[0][0])


# Algorithim to project future eps
def get_algo_eps_projection(ticker):
    html = make_yahoo_request(ticker)
    historic_actual_eps = get_historic_eps(html)

    #Analysts
    proj_analyst = float(get_estimated_future_eps(make_yahoo_request(ticker)))
    corr_analyst = float(correlation_estimates(ticker, historic_actual_eps))

    #Google Search
    proj_search = float(projection_google(ticker, historic_actual_eps))
    corr_search = float(correlation_google_trends(ticker, historic_actual_eps))

    #Insider Trends
    proj_insider = float(projection_insider(ticker, historic_actual_eps))
    corr_insider = float(correlation_insider(ticker, historic_actual_eps))


    projection = (proj_analyst*corr_analyst + proj_search*corr_search + proj_insider*corr_insider)/(corr_analyst + corr_search + corr_insider)
    return (projection)

# Returns information pertaining to a company's valuation
def get_company_health(ticker):
    stock = yf.Ticker(ticker)
    balance = stock.quarterly_balance_sheet
    #Market Cap -Assets +Liabillities
    assets_liabilites = []

    # Outstanding Shares
    shares_list = General.get_historic_shares(ticker)
    current_shares = stock.info["sharesOutstanding"]

    # Dates Earnings Filed
    finnhub_client = General.get_finnhub_client()
    financials_as_reported = finnhub_client.financials_reported(symbol=ticker, freq='quarterly')
    one_quarter_ago = datetime.strptime(financials_as_reported["data"][0]["acceptedDate"], "%Y-%m-%d %H:%M:%S")
    next_quarter = one_quarter_ago + relativedelta(months=3)
    two_quarters_ago = datetime.strptime(financials_as_reported["data"][1]["acceptedDate"], "%Y-%m-%d %H:%M:%S")
    three_quarters_ago = datetime.strptime(financials_as_reported["data"][2]["acceptedDate"], "%Y-%m-%d %H:%M:%S")
    four_quarters_ago = datetime.strptime(financials_as_reported["data"][3]["acceptedDate"], "%Y-%m-%d %H:%M:%S")

    # Initialize Dataframe to store values
    share_price = stock.history(start = four_quarters_ago, end = datetime.today(), interval = "1d", actions = False)["Close"]
    df = pd.DataFrame(share_price, columns = ["Close"])
    income_list = np.linspace(0,0, len(share_price))
    adj_marketcap_list = np.linspace(0,0, len(share_price))
    adj_earnings_list = np.linspace(0,0, len(share_price))

    #Get Future EPS Analyst Projection
    html = make_yahoo_request(ticker)
    stock_eps = html.find_all('tr')
    next_qtr = get_algo_eps_projection(ticker)
    future_qtr = float(stock_eps[2].find_all('td')[2].text)
    actual_eps = get_historic_eps(html)
    estimated_eps = get_historic_estimated_eps(html)[0:4]
    estimated_eps.append(next_qtr)
    estimated_eps.append(future_qtr)
    actual_eps.append(next_qtr)
    actual_eps.append(future_qtr)

    # Inititalize Projections
    for i in range(4):
        assets_liabilites.append(balance[balance.columns[3-i]][5] - balance[balance.columns[3-i]][2])

    # Add Values to Dataframe
    for i in range(len(df)):
        if (df.index[i] > one_quarter_ago):
            income_list[i] = round((actual_eps[3] + estimated_eps[4])*shares_list["Shares"][0] ,0)
            adj_marketcap_list[i] = df["Close"][i]*shares_list["Shares"][0] - assets_liabilites[3] 

        elif (df.index[i] > two_quarters_ago):
            income_list[i] = round((actual_eps[2] + estimated_eps[3])*shares_list["Shares"][1] ,0)
            adj_marketcap_list[i] = df["Close"][i]*shares_list["Shares"][1] - assets_liabilites[2] 

        elif (df.index[i] > three_quarters_ago):
            income_list[i] = round((actual_eps[1] + estimated_eps[2])*shares_list["Shares"][2] ,0)
            adj_marketcap_list[i] = df["Close"][i]*shares_list["Shares"][2] - assets_liabilites[1] 

        else:
            income_list[i] = round((actual_eps[0] + estimated_eps[1])*shares_list["Shares"][3] ,0)
            adj_marketcap_list[i] = df["Close"][i]*shares_list["Shares"][3] - assets_liabilites[0] 
        adj_earnings_list[i] = adj_marketcap_list[i]/income_list[i]
 
    avg_adjusted_earnings = sum(adj_earnings_list)/len(adj_earnings_list)
    adj_earnings_list = (adj_earnings_list/avg_adjusted_earnings)*50

    next_quarter_adj_marketcap = df["Close"][len(df)-1]*current_shares - assets_liabilites[3] + round((actual_eps[4])*current_shares ,0)
    next_earnings_valuation = ((next_quarter_adj_marketcap/(round((actual_eps[4] + estimated_eps[5])*current_shares ,0)))/avg_adjusted_earnings)*50

    return([df.index, adj_earnings_list, next_quarter, next_earnings_valuation, df["Close"][len(df)-1]])


# Displays a graph of a company's valuation
def update_valuation_chart(ticker):
    value = get_company_health(ticker)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=value[0], y = value[1],
                    mode='lines+markers',
                    name='Actual'))
    
    x_line = [value[0][len(value[0])-1], value[2]]
    y_line = [value[1][len(value[0])-1],value[3]]
    fig.add_trace(go.Scatter(x=x_line, y = y_line,
                    mode='lines+markers',
                    name='Projected'))

    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color = 'white')
    fig.update_yaxes(title = "Relative Valuation")
    fig.update_xaxes(title = "Date")
    fig.update_xaxes(tickangle = 0)
    fig.update_xaxes(showgrid = False)
    fig.update_layout(title = {
        'text': "Stock Valuation and Projection",
        'xanchor': 'center',
        'x': 0.5})
    return(fig)

