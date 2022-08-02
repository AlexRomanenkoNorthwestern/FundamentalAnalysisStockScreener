import General

# Import Libraries
import finnhub
from datetime import datetime, timedelta, date, time
from dateutil.relativedelta import relativedelta
import snscrape.modules.twitter as sntwitter
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
   
# Returns reddit message volume over the past month
def social_volume_reddit(ticker):
    today = datetime.now().strftime("%Y-%m-%d")
    one_month_ago = (datetime.now() + relativedelta(months=-1)).strftime("%Y-%m-%d")
    df = (General.get_finnhub_client().stock_social_sentiment(ticker, one_month_ago, today))['reddit']
    total_reddit = 0
    for i in range(len(df)):
        total_reddit += (int(df[i]['mention']))
    return(total_reddit)


# Returns a dataframe of information relating to tweets about a stock
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


# Returns the total volume of tweets for a ticker over a period of total_days
def find_tweets_volume(ticker, total_days):
    start_date =  datetime.today().date() - timedelta(days=total_days -1)
    end_date = datetime.today().date()
    return(len(list(sntwitter.TwitterSearchScraper('${} since:{} until:{}'.format(ticker, start_date, end_date)).get_items())))


# Returns the relative tweet volume for a ticker of the current week compared to the previous week
def relative_search_volume_twitter (ticker):
    two_week_count = find_tweets_volume(ticker,14)
    week_count = find_tweets_volume(ticker, 7)
    second_week_count= two_week_count-week_count
    result = ((week_count/second_week_count) - 1)*100
    if (result > 0):
        return ("+{}%".format(int(result)))
    else:
        return("{}%".format(int(result)))


# Displays a tweet volume graph
def tweets_volume_figure(ticker, total_days):
    start_date =  datetime.today().date() - timedelta(days=total_days -1)
    end_date = datetime.today().date()
    delta = timedelta(days=1)
    volume_list = []
    count = 0
    total = 0
    while start_date <= end_date:
        volume = len(list(sntwitter.TwitterSearchScraper(
                '${} since:{} until:{}'.format(ticker, start_date, start_date + delta)).get_items()))
        if (count < 7):
            count += 1
            total += volume
            volume_list.append([start_date, volume, total/count ])

        else:
            total = 0
            for i in range(6):
                total += volume_list[len(volume_list) - i -1][1]

            volume_list.append([start_date, volume, (total+volume)/7 ])
        start_date += delta


    tweets_df = pd.DataFrame(volume_list, columns=['Date', 'Tweet Volume', "7 Day Moving Average"])
    fig = px.bar(tweets_df, x = "Date", y = "Tweet Volume")
    fig.add_trace(go.Scatter(x = tweets_df['Date'], y = tweets_df["7 Day Moving Average"],
                    mode='lines+markers',
                    name='7 Day SMA',
                    marker_color = '#00CC96'))
    fig.update_layout(showlegend= False)
    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color = 'white')
    fig.update_xaxes(tickangle = 0)
    fig.update_layout(title = {
        'text': "Tweet Volume",
        'xanchor': 'center',
        'x': 0.5})
    return(fig)
