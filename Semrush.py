import General

# Import Libraries
import time
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup, element
import numpy as np
import math
import finnhub

def get_website_visits(ticker):
    try:
        company_url = General.get_finnhub_client().company_profile2(symbol= ticker)['weburl']
    except:
        time.sleep(5)
        company_url = General.get_finnhub_client().company_profile2(symbol= ticker)['weburl']
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
