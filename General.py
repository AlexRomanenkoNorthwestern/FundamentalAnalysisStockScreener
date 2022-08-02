# Import Libraries
import datetime as dt
import pandas as pd
from datetime import datetime, timedelta, date, time
import finnhub
import numpy as np
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
import yfinance as yf


# API Key for Finnhub
apiKey = "cbjm7biad3iarlnd4tmg"


# Initialize finnhub client
finnhub_client = finnhub.Client(api_key=apiKey)
finnhub_client.DEFAULT_TIMEOUT = 200


# Returns the finnhub_client to be used in other files
def get_finnhub_client():
    return(finnhub_client)


# Retrieves a stock ticker's company name and removes business types such as LLC, Ltd, Inc
def get_brand_name(ticker):
    ticker = str(ticker)
    try:
        company_name = finnhub_client.company_profile2(symbol= ticker)['name'].split(' ')
        company_name = company_name[0:len(company_name)-1]
        company_name = ' '.join(company_name)
    except:
        company_name = ticker
    return(company_name)


# Returns a stocks upcoming earnings date
def get_earnings_date(ticker):
    date = get_finnhub_client().company_earnings(ticker)[0]["period"]
    return(date)


# Retrieves a stock outstanding shares history for the past four quarters
def get_historic_shares(ticker):
    shares_url = 'https://ycharts.com/companies/'
    url = shares_url + ticker + '/shares_outstanding'
    req = Request(url=url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}) 
    response = urlopen(req)    
    html = BeautifulSoup(response, features="lxml")
    html = html.find_all('td')
    date_list = []
    shares_list = []
    one_quarter_ago = datetime.strptime(get_earnings_date(ticker), "%Y-%m-%d")
    two_quarters_ago = one_quarter_ago + relativedelta(months=-3)
    three_quarters_ago = one_quarter_ago + relativedelta(months=-6)
    four_quarters_ago = one_quarter_ago + relativedelta(months=-9)
    valid_dates = [one_quarter_ago.strftime('%Y-%m-%d'), two_quarters_ago.strftime('%Y-%m-%d'), 
                   three_quarters_ago.strftime('%Y-%m-%d'), four_quarters_ago.strftime('%Y-%m-%d')]
    for i in range(int(len(html)/2)):
        d = datetime.strptime(html[i*2].text, '%B %d, %Y')
        d = d.strftime('%Y-%m-%d')
        if(i>15):
            break
        elif (d in valid_dates):
            date_list.append(d)
            shares = html[(i*2)+1].text.replace(" ", "")
            shares = shares.replace("\n", "")
            if (shares[5] == 'T'):
                shares = float(shares[0:5]) * 1000
            elif (shares[5] == 'M'):
                shares = float(shares[0:5]) * 1000000
            elif (shares[5] == 'B'):
                shares = float(shares[0:5]) * 1000000000
            shares_list.append(shares)
    df = pd.DataFrame([date_list, shares_list]).transpose()
    df.columns = ["Date", "Shares"]
    return(df)
