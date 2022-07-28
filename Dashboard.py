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