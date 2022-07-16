import snscrape.modules.twitter as sntwitter
import snscrape.modules.reddit as snreddit
import pandas as pd
from datetime import timedelta, date, datetime
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import math
# pip install snscrape==0.4.2.20211215
# We cant use the latest version or there will be errors


# TWITTER
#-------------------------------------------------------------------------------------------------------------------------------------------------------------
# Returns a dataframe of recent tweets for a ticker over a period of the most recent total days
# Example: df = find_Tweets('$CROX', 5))
def find_Tweets(ticker, total_days):
    tweet_list = []

    start_date =  datetime.today().date() - timedelta(days=total_days -1)
    end_date = datetime.today()
    next_date = start_date + timedelta(days=1)
    delta = timedelta(days=1)

    sent = SentimentIntensityAnalyzer()
    while start_date <= end_date.date():
        for i,tweet in enumerate(sntwitter.TwitterSearchScraper('{} since:{} until:{}'.format(ticker, start_date, next_date)).get_items()):
            try:
                sentiment = sent.polarity_scores(tweet.content)
                tweet_list.append([tweet.date, tweet.user.displayname, tweet.user.followersCount, tweet.content, tweet.likeCount, sentiment])
            except Exception:
                pass
        start_date += delta
        next_date += delta

    tweets_df = pd.DataFrame(tweet_list, columns=['Datetime', 'User', 'Followers', 'Text', 'Likes', 'Sentiment'])
    return (tweets_df)



# Returns True if anyone with a specified minimum following has posted
# Example: large_following_post(df, 10000000)
def large_following_post(dataframe, minimum_followers):
    if (all(minimum_followers > (dataframe['Followers']))):
        return (False)
    else:
        return(True)



# Returns the average tweet sentiment levels for a given dataframe
# Example: sentiment(df)
def sentiment(dataframe):
    sum_negative = 0
    sum_neutral = 0
    sum_positive = 0

    for i in range(len(dataframe['Sentiment'])):
        sum_negative += (dataframe['Sentiment'][i].get('neg'))
        sum_neutral += (dataframe['Sentiment'][i].get('neu'))
        sum_positive += (dataframe['Sentiment'][i].get('pos'))
    return {'Negative': sum_negative/len(dataframe['Sentiment']), 'Neutral': sum_neutral/len(dataframe['Sentiment']), 'Positive': sum_positive/len(dataframe['Sentiment'])}



# Returns the number of twitter posts for a ticker
# Example: tweet_volume(df)
def tweet_volume(dataframe):
   return len(dataframe['Text'])



# Returns Relative Twitter Search Volume for a Search Term
# Compares the most recent 1/4 of a period to the other 3/4 of the period
# Returns a value from -100% to infinityt%
def relative_search_volume_twitter (dataframe):
    
    length = len(dataframe)
    first_three_fourths = math.floor(length*.75) - 1
    average_three_fourths = dataframe.iloc[1:first_three_fourths, 0].mean()

    average_current_quarter = dataframe.iloc[first_three_fourths:length, 0].mean()
    return ((average_current_quarter*100/average_three_fourths)-100)
