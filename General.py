from ast import Try
from pandas_datareader import data as pdr
import datetime as dt
import pandas as pd
import pytrends
from pytrends.request import TrendReq
pytrends = TrendReq()
from datetime import datetime, timedelta, date, time
import math
import plotly.graph_objects as go
import finnhub
import matplotlib.pyplot as plt
import numpy as np

from dateutil.relativedelta import relativedelta
import yfinance as yf
import snscrape.modules.twitter as sntwitter
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import math
import plotly.express as px


text_data = open("APIKey.txt", "r")
apiKey = text_data.readline()
apiKey = apiKey[0:len(apiKey)-1]
text_data.close()

# API Keys
finnhub_client = finnhub.Client(api_key=apiKey)

def get_finnhub_client():
    return(finnhub_client)

# Retrieves a stock ticker's company name and removes business types such as LLC, Ltd, Inc
# Example Usage: get_brand_name('CROX')
def get_brand_name(ticker):
    ticker = str(ticker)
    try:
        company_name = finnhub_client.company_profile2(symbol= ticker)['name'].split(' ')
        company_name = company_name[0:len(company_name)-1]
        company_name = ' '.join(company_name)
    except:
        company_name = ticker
    return(company_name)
