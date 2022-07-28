class Yahoo:
    
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