import Finviz
import Google
import Semrush
import Social
import Yahoo
import Social
import EarningsAlgo

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import yfinance as yf
from dash_extensions import Lottie       
import dash_bootstrap_components as dbc  
from dash_bootstrap_components._components.Container import Container
from datetime import date, datetime
import matplotlib.pyplot as plt
import numpy as np
import calendar
from wordcloud import WordCloud
import plotly.graph_objects as go


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
        dbc.Col([
            dbc.Card([
                    dbc.CardBody([
                        html.H4('Company Description'),
                        html.H6(id='description', children="Enter a stock ticker")
                        ])
                ], style={'borderRadius': '4px'}, color="dark")], width = 12),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([table], width = 6),
        dbc.Col([dbc.Card([
            dbc.CardBody([
                dcc.Graph(id='stock-chart', figure={}, config={'displayModeBar': False}),
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
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6('Google Trends'),
                    html.H2(id='google', children="000")
                ], style={'textAlign':'center'})
            ], style={'borderRadius': '4px'}, color="dark"),
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6('Insider Activity'),
                    html.H2(id='insider', children="000")
                ], style={'textAlign': 'center'})
            ], style={'borderRadius': '4px'}, color="dark"),
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6('Tweet Volume'),
                    html.H2(id='message', children="000")
                ], style={'textAlign': 'center'})
            ], style={'borderRadius': '4px'}, color="dark"),
        ], width=3),
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
                    dcc.Graph(id='value-chart', figure={}, config={'displayModeBar': False}),
                ])
            ], style={'borderRadius': '4px'}, color="dark"),
        ], width=6),
    ],className='mb-2'),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='tweet-chart', figure={}),
                ])
            ], style={'borderRadius': '4px'}, color="dark"),
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='google-chart', figure={}, config={'displayModeBar': False}),
                ])
            ], style={'borderRadius': '4px'}, color="dark"),
        ], width=8),
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
    Output('description','children'),
    Output('website','children'),
    Output('google','children'),
    Output('insider','children'),
    Output('message','children'),
    Output('table1','children'),
    Output('stock-chart','figure'),
    Output('line-chart','figure'),
    Output('value-chart','figure'),
    Output('tweet-chart','figure'),
    Output('google-chart','figure'),
    Output('search_button', 'n_clicks'),
    Input('search_bar','value'),
    Input('search_button', 'n_clicks'),
)
def update_small_cards(ticker, clicks):
    
    if (clicks>0):
        try:
            # Net Insider Transactions
            net_insider = Finviz.net_insider_transactions(ticker)
        except:
            return("NA", "NA", "NA", "NA", "NA", table_body, {}, {}, {}, {}, {}, 0)



        # Stock Description
        desc = yf.Ticker(ticker).info['longBusinessSummary']

        # Website Visits
        visits = Semrush.get_website_visits(ticker)

        # Google Trends
        g_df = Google.google_trends_dataframe(ticker, 365)
        g_trends = Google.relative_search_volume_google(g_df, 365)

        # Twitter Volume
        twitter = Social.relative_search_volume_twitter(ticker)

        # Stock Chart
        fig_stk = Yahoo.update_stk_chart(ticker)

        # Stock Table
        table_info = update_table(ticker)

        # EPS Bar Graph
        fig_eps = Yahoo.update_bar_eps(ticker)[0]
        
        # Valuation Graph
        fig_val = EarningsAlgo.update_valuation_chart(ticker)
        
        # Tweets Graph
        fig_tweets = Social.tweets_volume_figure(ticker, 14)

        # Google Trends Graph
        fig_google = Google.google_trends_graph(Google.google_trends_dataframe(ticker, 730))

        clicks = 0
        return desc, visits, g_trends, net_insider, twitter, table_info, fig_stk, fig_eps, fig_val, fig_tweets, fig_google, clicks

    
if __name__=='__main__':
    app.run_server(debug=False, port=8004)
