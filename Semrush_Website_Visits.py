from urllib.request import urlopen, Request
from bs4 import BeautifulSoup, element
import pandas as pd
import finnhub

# API Keys
finnhub_client = finnhub.Client(api_key="INSERT_API_KEY")

# Returns a dataframe with projected website visitors over the past 3 months
# Example Usage: get_website_visits('CROX')
def get_website_visits(ticker):
    company_url = finnhub_client.company_profile2(symbol= ticker)['weburl']
    company_url = company_url.replace('https://','')
    company_url = company_url.replace('www.','')
    company_url, sep, after = company_url.partition('/')
    while(company_url.count('.') > 1):
        before, sep, company_url = company_url.partition('.')
    semrush_url = 'https://www.semrush.com/website/' + company_url +'/overview/'
    try:
      req = Request(url=semrush_url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}) 
      response = urlopen(req)    
      html = BeautifulSoup(response, features="lxml")
      visit_list = []
      month = html.find_all('span')[72].text
      visits = html.find_all('span')[73].text
      visit_list.append([month,visits])
      month = html.find_all('span')[74].text
      visits = html.find_all('span')[75].text
      visit_list.append([month,visits])
      month = html.find_all('span')[76].text
      visits = html.find_all('span')[77].text
      visit_list.append([month,visits])
      df = pd.DataFrame(visit_list, columns = ['Date', 'Visits'])
    except:
      print('Stock ticker not found')
    return(df)
#print (get_website_visits('CROX'))


