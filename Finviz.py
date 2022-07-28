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
