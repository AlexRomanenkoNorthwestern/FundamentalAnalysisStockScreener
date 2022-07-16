# FINVIZ NEWS HEADLINES, ANALYST PRICE TARGETS, INSIDER TRANSACTIONS
#-------------------------------------------------------------------------------------------------------------------------------------------------------------
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import os
import matplotlib.pyplot as plt


# Returns sentiment from news headlines of the 5 most recent news articles
def news_headlines_sentiment(ticker):
    finviz_url = 'https://finviz.com/quote.ashx?t='
    url = finviz_url + ticker
    req = Request(url=url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}) 
    response = urlopen(req)    
    
    # Read the contents of the file into 'html'
    html = BeautifulSoup(response, features="lxml")

    # Find 'news-table' in the Soup and load it into 'news_table'
    news_table = html.find(id='news-table')

    # Get all the table rows tagged in HTML with <tr> into ‘amzn_tr’
    stock_tr = news_table.findAll('tr')
    sum_positive = 0
    sum_neutral = 0
    sum_negative = 0
    count = 0
    sent = SentimentIntensityAnalyzer()
    for i, table_row in enumerate(stock_tr):

        # Read the text of the element ‘a’ into ‘link_text’
        text = table_row.a.text

        #Only include articles with ticker name
        if ticker in text:
            sentiment = sent.polarity_scores(text)
            sum_negative += (sentiment.get('neg'))
            sum_neutral += (sentiment.get('neu'))
            sum_positive += (sentiment.get('pos'))
            count += 1

        if count == 5:
            break

    if count ==0:
        count = 1

    return {'Negative': sum_negative/count, 'Neutral': sum_neutral/count, 'Positive': sum_positive/count}
# print(news_headlines_sentiment('CROX'))



def analyst_price_target_changes(ticker, total_days):
    finviz_url = 'https://finviz.com/quote.ashx?t='
    url = finviz_url + ticker
    req = Request(url=url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}) 
    response = urlopen(req)    
    
    # Read the contents of the file into 'html'
    html = BeautifulSoup(response, features="lxml")

    # Find 'news-table' in the Soup and load it into 'news_table'
    stock_tr = html.find(class_='fullview-ratings-outer').find_all('tr')

    news_list = []

    for i, table_row in enumerate(stock_tr):

        # Read the text of the element ‘a’ into ‘link_text’
        date = table_row.find_all('td')[0].text
        date_vector = date.split()
        date_vector[0] = date_vector[0].replace('Initiated', '')
        date_vector[0] = date_vector[0].replace('Upgrade', '')
        date_vector[0] = date_vector[0].replace('Downgrade', '')
        date_vector[0] = date_vector[0].replace('Reiterated', '')
        text = table_row.find_all('td')[4].text
        text_vector = text.split()
        if '$' in text:
            if len(text_vector) == 3:
                Date = date_vector[0]
                Percent_Change = ((int(text_vector[2].replace('$','')) - (int(text_vector[0].replace('$',''))))/(int(text_vector[0].replace('$',''))))*100
                news_list.append([Date, Percent_Change])
    df = pd.DataFrame(news_list, columns=['Date', 'Percent_Change'])
    print(df)
    return (df)
#analyst_price_target_changes('CROX', 30)


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
    del insider['SEC Form 4']
    return insider
#print(insider_transactions('CROX'))
