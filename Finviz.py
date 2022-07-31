import General

# Import Libraries
from dateutil.relativedelta import relativedelta
import yfinance as yf
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup, element
import pandas as pd
from datetime import datetime, timedelta, date, time
import finnhub
import time
import plotly.express as px
import plotly.graph_objects as go


# Used for a table
def insider_transactions(ticker):
    finviz_url = 'https://finviz.com/quote.ashx?t='
    url = finviz_url + ticker
    req = Request(url=url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}) 
    response = urlopen(req)    
    
    # Read the contents of the file into 'html'
    html = BeautifulSoup(response, features="lxml")
    insider = pd.read_html(str(html), attrs = {'class': 'body-table'})[0]
        
    # Clean up insider dataframe
    insider = insider.iloc[1:]
    insider.columns = ['Trader', 'Relationship', 'Date', 'Transaction', 'Cost', '# Shares', 'Value ($)', '# Shares Total', 'SEC Form 4']
    insider = insider[['Date', 'Trader', 'Relationship', 'Transaction', 'Cost', '# Shares', 'Value ($)', '# Shares Total', 'SEC Form 4']]
    insider = insider.set_index('Date')
    del insider['Trader']
    del insider['Relationship']
    del insider['Cost']
    del insider['# Shares Total']
    del insider['Value ($)']
    del insider['SEC Form 4']
    return insider

# net insider transactions over the past three months
def net_insider_transactions(ticker):
    today = datetime.now().strftime("%Y-%m-%d")
    three_months_ago = (datetime.now() + relativedelta(months=-3)).strftime("%Y-%m-%d")
    try:
        df = General.get_finnhub_client().stock_insider_transactions(ticker, three_months_ago, today)['data']
    except:
        time.sleep(3)
        df = General.get_finnhub_client().stock_insider_transactions(ticker, three_months_ago, today)['data']

    net = 0
    for i in range(len(df)):
        net += (int(df[i]['change']))
    stock = yf.Ticker(ticker)
    out = stock.info['sharesOutstanding']
    result = round(net/out*100,4)
    if (result > 0):
        return ("+{}%".format(result))
    else:
        return("{}%".format(result))

def insider_chart(ticker):
    today = datetime.now().strftime("%Y-%m-%d")
    three_months_ago = (datetime.now() + relativedelta(months=-3)).strftime("%Y-%m-%d")
    try:
        df = General.get_finnhub_client().stock_insider_transactions(ticker, three_months_ago, today)['data']
    except:
        time.sleep(3)
        df = General.get_finnhub_client().stock_insider_transactions(ticker, three_months_ago, today)['data']

    positive_sum = 0
    negative_sum = 0
    for i in range(len(df)):
        if ((int(df[i]['change'])) > 0):
            positive_sum += int(df[i]['change'])
        else:
            negative_sum += abs(int(df[i]['change']))
    
    fig = px.pie(values = [positive_sum, negative_sum], names = ["Positive", "Negative"], hole = 0.5)
    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20),
                          paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)',
                          font_color = 'white')
    return(fig)

