# FUNCTIONS FOR DATA MANAGEMENT  **************************
from ast import Try
from pandas_datareader import data as pdr
import datetime as dt
import pandas as pd
import pytrends
from pytrends.request import TrendReq
pytrends = TrendReq()
from datetime import datetime, timedelta, date
import math
import plotly.graph_objects as go
import finnhub

# API Keys
finnhub_client = finnhub.Client(api_key="cb7kvuiad3i5ufvorpb0")

# SEMRUSH WEBSITE VISITS
#-------------------------------------------------------------------------------------------------------------------------------------------------------------
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup, element
import os
import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import numpy as np
import time


def get_website_visits(ticker):
    finnhub_client = finnhub.Client(api_key="cb7kvuiad3i5ufvorpb0")
    try:
        company_url = finnhub_client.company_profile2(symbol= ticker)['weburl']
    except:
        time.sleep(5)
        company_url = finnhub_client.company_profile2(symbol= ticker)['weburl']
    company_url = company_url.replace('https://','')
    company_url = company_url.replace('http://','')
    company_url = company_url.replace('www.','')
    company_url, sep, after = company_url.partition('/')
    while(company_url.count('.') > 1):
        before, sep, company_url = company_url.partition('.')
    semrush_url = 'https://www.semrush.com/website/' + company_url +'/overview/'
    req = Request(url=semrush_url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}) 
    try:
        response = urlopen(req)    
    except:
        return "NA"
    html = BeautifulSoup(response, features="lxml")
    visit_list = []
    month_list = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    index = 0
    for i in np.linspace(55,70):
        if (html.find_all('span')[int(i)].text in month_list):
            index = i
            break

    visits = html.find_all('span')[int(index+1)].text
    visits1 = float([visits[:-1]][0])
    visits = html.find_all('span')[int(index+3)].text
    visits2 = float([visits[:-1]][0])
    visits = html.find_all('span')[int(index+5)].text
    visits3 = float([visits[:-1]][0])
    
    # Simple Math Exponential Decay/ Growth: Change to more advanced model later
    result = (math.sqrt(visits1/visits3) - 1) *100
    if (result > 0):
        return ("+{}%".format(int(result)))
    else:
        return("{}%".format(int(result)))


# GOOGLE TRENDS
#-------------------------------------------------------------------------------------------------------------------------------------------------------------
# Retrieves a stock ticker's company name and removes business types such as LLC, Ltd, Inc
# Example Usage: get_brand_name('CROX')
def get_brand_name (ticker):
  ticker = str(ticker)
  try:
    company_name = finnhub_client.company_profile2(symbol= ticker)['name'].split(' ')
  except:
    company_name = ticker
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


# Insider Transactions
#-------------------------------------------------------------------------------------------------------------------------------------------------------------
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

from dateutil.relativedelta import relativedelta
import yfinance as yf
# net insider transactions over the past three months
def net_insider_transactions(ticker):
    today = datetime.now().strftime("%Y-%m-%d")
    three_months_ago = (datetime.now() + relativedelta(months=-3)).strftime("%Y-%m-%d")
    df = finnhub_client.stock_insider_transactions(ticker, three_months_ago, today)['data']
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


# Twitter and Reddit
#-------------------------------------------------------------------------------------------------------------------------------------------------------------
import snscrape.modules.twitter as sntwitter
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import math
# pip install snscrape==0.4.2.20211215

def social_volume_reddit(ticker):
    today = datetime.now().strftime("%Y-%m-%d")
    one_month_ago = (datetime.now() + relativedelta(months=-1)).strftime("%Y-%m-%d")
    df = (finnhub_client.stock_social_sentiment(ticker, one_month_ago, today))['reddit']
    total_reddit = 0
    for i in range(len(df)):
        total_reddit += (int(df[i]['mention']))
    return(total_reddit)

def find_tweets(ticker, total_days):
    tweet_list = []
    start_date =  datetime.today().date() - timedelta(days=total_days -1)
    end_date = datetime.today()
    next_date = start_date + timedelta(days=1)
    delta = timedelta(days=1)

    sent = SentimentIntensityAnalyzer()
    while start_date <= end_date.date():
        for i,tweet in enumerate(sntwitter.TwitterSearchScraper('${} since:{} until:{}'.format(ticker, start_date, next_date)).get_items()):
            try:
                sentiment = sent.polarity_scores(tweet.content)
                tweet_list.append([tweet.date.date(), tweet.user.displayname, tweet.user.followersCount, tweet.content, tweet.likeCount, sentiment])
            except Exception:
                pass
        start_date += delta
        next_date += delta

    tweets_df = pd.DataFrame(tweet_list, columns=['Date', 'User', 'Followers', 'Text', 'Likes', 'Sentiment'])
    return (tweets_df)

def find_tweets_volume(ticker, total_days):
    start_date =  datetime.today().date() - timedelta(days=total_days -1)
    end_date = datetime.today().date()
    return(len(list(sntwitter.TwitterSearchScraper('${} since:{} until:{}'.format(ticker, start_date, end_date)).get_items())))
     
def social_volume_twitter(ticker):
    days =  (datetime.now()-(datetime.now() + relativedelta(months=-1))).days
    df = find_tweets_volume(ticker,days)
    return(len(df))

def relative_search_volume_twitter (ticker):
    return(0)
    two_week_count = find_tweets_volume(ticker,14)
    week_count = find_tweets_volume(ticker, 7)
    second_week_count= two_week_count-week_count
    result = ((week_count/second_week_count) - 1)*100
    if (result > 0):
        return ("+{}%".format(int(result)))
    else:
        return("{}%".format(int(result)))



# SafeGraph FootTraffic
#-------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_footraffic(brand):
    if (brand =='crocs'):
        return(0)
    else:
        return("NA")


# YAHOO STOCK Financials
#-------------------------------------------------------------------------------------------------------------------------------------------------------------
import plotly.express as px
import matplotlib.pyplot as plt

def make_yahoo_request(ticker):
    yahoo_url = 'https://finance.yahoo.com/quote/' + ticker + '/analysis?p=' + ticker
    req = Request(url=yahoo_url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}) 
    response = urlopen(req)
    html = BeautifulSoup(response, features="lxml")
    return(html)

def get_algo_estimated_eps(ticker):

    return(0)

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
    df = pd.DataFrame(eps_list, columns=['Actual EPS'])
    return(eps_list)

# Next quarter Analyst EPS
def get_estimated_future_eps(html):
    # Read the contents of the file into 'html'
    stock_eps = html.find_all('tr')
    eps_list = []
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
    df = pd.DataFrame(eps_list, columns=['Analyst Estimated EPS'])
    return(eps_list)


def update_bar_eps(ticker):
    html = make_yahoo_request(ticker)
 

    x = ["One Year Ago","Three Quarers Ago","Two Quarters Ago","Last Quarter","Next Quarter"]
    y_historic = get_historic_eps(html, ticker)
    y_estimated = get_historic_estimated_eps(html)
    x_axis = np.arange(len(x))

    plt.bar(x_axis - 0.15, y_estimated, width = 0.3, label = "Estimated EPS", color = 'blue')
    plt.bar(x_axis + 0.15, y_historic, width = 0.3, label = "Actual EPS", color = 'green')
    plt.xticks(x_axis, x)
    plt.xlabel("Quarter")
    plt.ylabel("EPS")
    plt.title("EPS History and Projections")
    plt.legend()
    plt.figure().patch.set_alpha(0)
    plt.axes().set_alpha(0)
    plt.show()


    
update_bar_eps("CROX")
















# Dashboard
#-------------------------------------------------------------------------------------------------------------------------------------------------------------
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import yfinance as yf
from dash_extensions import Lottie       # pip install dash-extensions
import dash_bootstrap_components as dbc  # pip install dash-bootstrap-components
from dash_bootstrap_components._components.Container import Container
from datetime import date
import calendar
from wordcloud import WordCloud          # pip install wordcloud



options = dict(loop=True, autoplay=True, rendererSettings=dict(preserveAspectRatio='xMidYMid slice'))
# Import App data from csv sheets **************************************
df_cnt = pd.read_csv("https://raw.githubusercontent.com/Coding-with-Adam/Dash-by-Plotly/master/Analytic_Web_Apps/Linkedin_Analysis/Connections.csv")
df_cnt["Connected On"] = pd.to_datetime(df_cnt["Connected On"])
df_cnt["month"] = df_cnt["Connected On"].dt.month
df_cnt['month'] = df_cnt['month'].apply(lambda x: calendar.month_abbr[x])

df_invite = pd.read_csv("https://raw.githubusercontent.com/Coding-with-Adam/Dash-by-Plotly/master/Analytic_Web_Apps/Linkedin_Analysis/Invitations.csv")
df_invite["Sent At"] = pd.to_datetime(df_invite["Sent At"])

df_react = pd.read_csv("https://raw.githubusercontent.com/Coding-with-Adam/Dash-by-Plotly/master/Analytic_Web_Apps/Linkedin_Analysis/Reactions.csv")
df_react["Date"] = pd.to_datetime(df_react["Date"])

df_msg = pd.read_csv("https://raw.githubusercontent.com/Coding-with-Adam/Dash-by-Plotly/master/Analytic_Web_Apps/Linkedin_Analysis/messages.csv")
df_msg["DATE"] = pd.to_datetime(df_msg["DATE"])





# NAVIGATION BAR/SEARCH BAR **************************************
PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"
search_bar = dbc.Row(
    [
        dbc.Col(dbc.Input(id = "search_bar", value="AAPL", type="text")),
        dbc.Col(dbc.Button("Search", id = "search_button", color="primary", className="ms-2", n_clicks=0), width="auto",),
    ],
    style={'height': '6%', 'width': '30%'},
    className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=PLOTLY_LOGO, height="40px")),
                        dbc.Col(dbc.NavbarBrand("Stock Analytics", className="ms-2")),
                    ],
                    align="center",
                    className="g-0",
                ),
                style={"textDecoration": "none",'position': 'fixed','z-index':'999', 'left': '13px'},
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(
                search_bar,
                id="navbar-collapse",
                is_open=False,
                navbar=True,
            ),
        ]
    ),
    style={'position': 'fixed','z-index':'999', 'height': '8%'},
    color="dark",
    dark=True,
 
)

#TABLE WITH STOCK INFORMATION **************************************
row1 = html.Tr([html.Td("Symbol"), html.Td("NA")]) #symbol
row2 = html.Tr([html.Td("Market Capitalization"), html.Td("NA")]) #marketCap
row3 = html.Tr([html.Td("Outstanding Shares"), html.Td("NA")]) # sharesOutstanding
row4 = html.Tr([html.Td("Float"), html.Td("NA")]) #floatShares
row5 = html.Tr([html.Td("Average Daily Volume (10 Days)"), html.Td("NA")]) #AverageDailyVolume10Days
row6 = html.Tr([html.Td("Insider Ownership"), html.Td("NA")]) #heldPercentInsiders
row7 = html.Tr([html.Td("Institutional Ownership"), html.Td("NA")]) #heldPercentInstitution
row8 = html.Tr([html.Td("Book Value"), html.Td("NA")]) #bookValue
row9 = html.Tr([html.Td("P/E Ratio"), html.Td("NA")]) #trailingPE
row10 = html.Tr([html.Td("Employees"), html.Td("NA")]) #fullTimeEmployees
row11 = html.Tr([html.Td("Sector"), html.Td("NA")]) #sector
row12 = html.Tr([html.Td("Exchange"), html.Td("NA")]) #exchange

table_body = [html.Tbody([row1, row2, row3, row4, row5, row6, row7, row8, row9, row10, row11, row12])]
table = dbc.Card([dbc.CardBody([dbc.Table(table_body, id = 'table1', bordered=True)])], style={ 'borderRadius': '4px'}, color="dark")




# LAYOUT **************************************
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO])
app.layout = dbc.Container([
    dbc.Row([
        navbar
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.DatePickerSingle(
                        id='my-date-picker-start',
                        date=date(2018, 1, 1),
                        className='ml-5'
                    ),
                    dcc.DatePickerSingle(
                        id='my-date-picker-end',
                        date=date(2021, 4, 4),
                        className='mb-2 ml-2'
                    ),
                ])
            ], color="dark", style={'top': '-20px', 'height':'2vh'}),
        ], width=12),
    ],className='mb-2 mt-2'),
    html.Br(),
    html.Br(),
    dbc.Row([
        dbc.Col([table], width = 6),
        dbc.Col([dbc.Card([
            dbc.CardBody([
                dcc.Graph(id='line-chart1', figure={}, config={'displayModeBar': False}),
                ])
            ], style={'height': '59.6vh', 'borderRadius': '4px'}, color="dark")], width = 6),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6('Website Visitors'),
                    html.H2(id='website', children="000")
                ], style={'textAlign':'center'})
            ], style={'borderRadius': '4px'}, color="dark"),
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6('Google Trends'),
                    html.H2(id='google', children="000")
                ], style={'textAlign':'center'})
            ], style={'borderRadius': '4px'}, color="dark"),
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6('Foot Traffic'),
                    html.H2(id='foot', children="000")
                ], style={'textAlign':'center'})
            ], style={'borderRadius': '4px'}, color="dark"),
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6('Insider Activity'),
                    html.H2(id='insider', children="000")
                ], style={'textAlign': 'center'})
            ], style={'borderRadius': '4px'}, color="dark"),
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6('Tweet Volume'),
                    html.H2(id='message', children="000")
                ], style={'textAlign': 'center'})
            ], style={'borderRadius': '4px'}, color="dark"),
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6('Analyst Sentiment'),
                    html.H2(id='analyst', children="000")
                ], style={'textAlign': 'center'})
            ], style={'borderRadius': '4px'}, color="dark"),
        ], width=2),

    ], className='mb-2'),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='line-chart', figure={}, config={'displayModeBar': False}),
                ])
            ], style={'borderRadius': '4px'}, color="dark"),
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='bar-chart', figure={}, config={'displayModeBar': False}),
                ])
            ], style={'borderRadius': '4px'}, color="dark"),
        ], width=6),
    ],className='mb-2'),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='TBD', figure={}),
                ])
            ], style={'borderRadius': '4px'}, color="dark"),
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='pie-chart', figure={}, config={'displayModeBar': False}),
                ])
            ], style={'borderRadius': '4px'}, color="dark"),
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='wordcloud', figure={}, config={'displayModeBar': False}),
                ])
            ], style={'borderRadius': '4px'}, color="dark"),
        ], width=4),
    ],className='mb-2'),
], fluid=True)


# Updating Table ******************************************
def update_table(ticker):
    stk = yf.Ticker(ticker).info
    try:
        row1 = html.Tr([html.Td("Symbol"), html.Td(stk['symbol'])]) 
    except:
        row1 = html.Tr([html.Td("Symbol"), html.Td('NA')]) 
    try:
        row2 = html.Tr([html.Td("Market Capitalization"), html.Td('{:,}'.format(stk['marketCap']))])
    except:
        row2 = html.Tr([html.Td("Market Capitalization"), html.Td('NA')])
    try:
        row3 = html.Tr([html.Td("Outstanding Shares"), html.Td('{:,}'.format(stk['sharesOutstanding']))]) 
    except:
        row3 = html.Tr([html.Td("Outstanding Shares"), html.Td('NA')]) 
    try:
        row4 = html.Tr([html.Td("Float"), html.Td('{:,}'.format(stk['floatShares']))])  
    except:
        row4 = html.Tr([html.Td("Float"), html.Td('NA')])
    try:
        row5 = html.Tr([html.Td("Average Daily Volume (10 Days)"), html.Td('{:,}'.format(stk['averageDailyVolume10Day']))])
    except:
        row5 = html.Tr([html.Td("Average Daily Volume (10 Days)"), html.Td('NA')])
    try:
        row6 = html.Tr([html.Td("Insider Ownership"), html.Td(round(stk['heldPercentInsiders']*100,1))])
    except:
        row6 = html.Tr([html.Td("Insider Ownership"), html.Td('NA')])
    try:
        row7 = html.Tr([html.Td("Institutional Ownership"), html.Td(round(stk['heldPercentInstitutions']*100,1))]) 
    except:
        row7 = html.Tr([html.Td("Institutional Ownership"), html.Td('NA')]) 
    try:
        row8 = html.Tr([html.Td("Book Value"), html.Td(stk['bookValue'])]) 
    except:
        row8 = html.Tr([html.Td("Book Value"), html.Td('NA')]) 
    try:
        row9 = html.Tr([html.Td("P/E Ratio"), html.Td(round(stk['trailingPE'],1))]) 
    except:
        row9 = html.Tr([html.Td("P/E Ratio"), html.Td('NA')]) 
    try:
        row10 = html.Tr([html.Td("Employees"), html.Td('{:,}'.format(stk['fullTimeEmployees']))])
    except:
        row10 = html.Tr([html.Td("Employees"), html.Td('NA')])
    try:
         row11 = html.Tr([html.Td("Sector"), html.Td(stk['sector'])])
    except:
         row11 = html.Tr([html.Td("Sector"), html.Td('NA')])
    try:
        row12 = html.Tr([html.Td("Exchange"), html.Td(stk['exchange'])]) 
    except:
        row12 = html.Tr([html.Td("Exchange"), html.Td('NA')]) 
    table_body = [html.Tbody([row1, row2, row3, row4, row5, row6, row7, row8, row9, row10, row11, row12])]
    return table_body



# Updating the 6 number cards and table ******************************************
@app.callback(
    Output('website','children'),
    Output('google','children'),
    Output('foot','children'),
    Output('insider','children'),
    Output('message','children'),
    Output('analyst','children'),
    Output('table1','children'),
    Output('search_button', 'n_clicks'),
    Input('my-date-picker-start','date'),
    Input('my-date-picker-end','date'),
    Input('search_bar','value'),
    Input('search_button', 'n_clicks'),
)
def update_small_cards(start_date, end_date, ticker, clicks):
    visits = 0
    compns_num = 0
    g_trends = 0
    net_insider = 0
    twitter = 0
    reactns_num = 0
    
    if (clicks>0):
        # Connections
        dff_c = df_cnt.copy()

        dff_c = dff_c[(dff_c['Connected On']>=start_date) & (dff_c['Connected On']<=end_date)]
        compns_num = len(dff_c['Company'].unique())
        compns_num = ticker

        # Website Visits
        visits = get_website_visits(ticker)

        # Google Trends
        g_df = google_trends_dataframe(ticker, 365)
        g_trends = relative_search_volume_google(g_df, 365)

        # Net Insider Transactions
        net_insider = net_insider_transactions(ticker)

        # Twitter Volume
        twitter = relative_search_volume_twitter(ticker)

        # Invitations
        dff_i = df_invite.copy()
        dff_i = dff_i[(dff_i['Sent At']>=start_date) & (dff_i['Sent At']<=end_date)]
        # print(dff_i)
        

        # Reactions
        dff_r = df_react.copy()
        dff_r = dff_r[(dff_r['Date']>=start_date) & (dff_r['Date']<=end_date)]
        reactns_num = len(dff_r)

        table_info = update_table(ticker)
      
        
        clicks = 0
        return visits, g_trends, compns_num, net_insider, twitter, reactns_num, table_info, clicks




# Line Chart ***********************************************************
@app.callback(
    Output('line-chart','figure'),
    Input('my-date-picker-start','date'),
    Input('my-date-picker-end','date'),
    #Input('search_bar','value'),
)
def update_line(start_date, end_date):
    #df = google_trends_dataframe(ticker, 180)
    #return google_trends_graph(df)
    dff = df_cnt.copy()
    dff = dff[(dff['Connected On']>=start_date) & (dff['Connected On']<=end_date)]
    dff = dff[["month"]].value_counts()
    dff = dff.to_frame()
    dff.reset_index(inplace=True)
    dff.rename(columns={0: 'Total connections'}, inplace=True)

    fig_line = px.line(dff, x='month', y='Total connections', template='ggplot2',
                  title="Total Connections by Month Name")
    fig_line.update_traces(mode="lines+markers", fill='tozeroy',line={'color':'blue'})
    fig_line.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color = 'white')
    fig_line.update_xaxes(showgrid=False)
    fig_line.update_yaxes(showgrid=False)
    fig_line.update_xaxes(showline=False)
    fig_line.update_yaxes(showline=False)
    fig_line.update_xaxes(zeroline=False)
    fig_line.update_yaxes(zeroline=False)
    return fig_line

# Line Chart ***********************************************************
@app.callback(
    Output('line-chart1','figure'),
    Input('my-date-picker-start','date'),
    Input('my-date-picker-end','date'),
    #Input('search_bar','value'),
)
def update_line1(start_date, end_date):
    #df = google_trends_dataframe(ticker, 180)
    #return google_trends_graph(df)
    dff = df_cnt.copy()
    dff = dff[(dff['Connected On']>=start_date) & (dff['Connected On']<=end_date)]
    dff = dff[["month"]].value_counts()
    dff = dff.to_frame()
    dff.reset_index(inplace=True)
    dff.rename(columns={0: 'Total connections'}, inplace=True)

    fig_line = px.line(dff, x='month', y='Total connections', template='ggplot2',
                  title="Total Connections by Month Name")
    fig_line.update_traces(mode="lines+markers", fill='tozeroy',line={'color':'blue'})
    fig_line.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color = 'white')
    fig_line.update_xaxes(showgrid=False)
    fig_line.update_yaxes(showgrid=False)
    fig_line.update_xaxes(showline=False)
    fig_line.update_yaxes(showline=False)
    fig_line.update_xaxes(zeroline=False)
    fig_line.update_yaxes(zeroline=False)
    return fig_line


# Bar Chart ************************************************************
@app.callback(
    Output('bar-chart','figure'),
    Input('my-date-picker-start','date'),
    Input('my-date-picker-end','date'),
)
def update_bar(start_date, end_date):
    dff = df_cnt.copy()
    dff = dff[(dff['Connected On']>=start_date) & (dff['Connected On']<=end_date)]

    dff = dff[["Company"]].value_counts().head(6)
    dff = dff.to_frame()
    dff.reset_index(inplace=True)
    dff.rename(columns={0:'Total connections'}, inplace=True)
    # print(dff_comp)
    fig_bar = px.bar(dff, x='Total connections', y='Company', template='ggplot2',
                      orientation='h', title="Total Connections by Company")
    fig_bar.update_yaxes(tickangle=45)
    fig_bar.update_layout(margin=dict(l=20, r=20, t=30, b=20),
                          paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)',
                          font_color = 'white')
    fig_bar.update_traces(marker_color='blue')
    fig_bar.update_xaxes(showgrid=False)
    fig_bar.update_yaxes(showgrid=False)
    fig_bar.update_xaxes(showline=False)
    fig_bar.update_yaxes(showline=False)
    fig_bar.update_xaxes(zeroline=False)
    fig_bar.update_yaxes(zeroline=False)

    return fig_bar


# Pie Chart ************************************************************
@app.callback(
    Output('pie-chart','figure'),
    Input('my-date-picker-start','date'),
    Input('my-date-picker-end','date'),
)
def update_pie(start_date, end_date):
    dff = df_msg.copy()
    dff = dff[(dff['DATE']>=start_date) & (dff['DATE']<=end_date)]
    msg_sent = len(dff[dff['FROM']=='Adam Schroeder'])
    msg_rcvd = len(dff[dff['FROM'] != 'Adam Schroeder'])
    fig_pie = px.pie(names=['Sent','Received'], values=[msg_sent, msg_rcvd],
                     template='ggplot2', title="Messages Sent & Received"
                     )
    fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
    fig_pie.update_traces(marker_colors=['red','blue'])

    return fig_pie


# Word Cloud ************************************************************
@app.callback(
    Output('wordcloud','figure'),
    Input('my-date-picker-start','date'),
    Input('my-date-picker-end','date'),
)
def update_pie(start_date, end_date):
    dff = df_cnt.copy()
    dff = dff.Position[(dff['Connected On']>=start_date) & (dff['Connected On']<=end_date)].astype(str)

    my_wordcloud = WordCloud(
        background_color='white',
        height=275
    ).generate(' '.join(dff))

    fig_wordcloud = px.imshow(my_wordcloud, template='ggplot2',
                              title="Total Connections by Position")
    fig_wordcloud.update_layout(margin=dict(l=20, r=20, t=30, b=20))
    fig_wordcloud.update_xaxes(visible=False)
    fig_wordcloud.update_yaxes(visible=False)

    return fig_wordcloud













if __name__=='__main__':
    app.run_server(debug=False, port=8004)
