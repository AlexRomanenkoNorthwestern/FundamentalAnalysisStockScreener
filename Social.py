class Social:
   
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