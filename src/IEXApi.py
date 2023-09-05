import requests


class IEXCloudQuote:
    BASE_URL = 'https://cloud.iexapis.com/stable/stock/{}/quote?token={}'
    TOKEN = 'YOUR_IEX_CLOUD_API_TOKEN'

    def __init__(self, ticker_symbol):
        self.ticker_symbol = ticker_symbol
        self.url = self.BASE_URL.format(ticker_symbol, self.TOKEN)
        self.current_price = None
        self.market_cap = None
        self.name = None
        self.average_volume = None
        self.ttm_eps = None

    def fetch_quote(self):
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                data = response.json()
                self.current_price = data.get('latestPrice')
                self.market_cap = data.get('marketCap')
                self.name = data.get('companyName')
                self.average_volume = data.get('avgTotalVolume')
                self.ttm_eps = data.get('ttmEPS')
                return True
        except:
            pass
        return False


class IEXCloudAnalysis:
    BASE_URL = 'https://cloud.iexapis.com/stable/stock/{}/recommendation-trends?token={}'
    TOKEN = 'YOUR_IEX_CLOUD_API_TOKEN'

    def __init__(self, ticker_symbol):
        self.ticker_symbol = ticker_symbol
        self.url = self.BASE_URL.format(ticker_symbol, self.TOKEN)
        self.five_year_growth_rate = None

    def fetch_five_year_growth_rate(self):
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                data = response.json()
                for trend in data:
                    if trend['period'] == '5y':
                        self.five_year_growth_rate = trend['ratingBuy']
                        return True
        except:
            pass
        return False


class IEXCloudQuoteSummary:
    BASE_URL = 'https://cloud.iexapis.com/stable/stock/{}/advanced-stats?token={}'
    TOKEN = 'YOUR_IEX_CLOUD_API_TOKEN'

    def __init__(self, ticker_symbol, modules):
        self.ticker_symbol = ticker_symbol
        self.url = self.BASE_URL.format(ticker_symbol, self.TOKEN)
        self.modules = modules
        self.module_data = {}

    def fetch_modules(self):
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                data = response.json()
                for module in self.modules:
                    self.module_data[module] = data.get(module)
                return True
        except:
            pass
        return False

    def get_balance_sheet_history(self, key):
        history = []
        balance_sheet = self.module_data.get('balanceSheetHistory', {}).get('balanceSheetStatements', [])
        for stmt in balance_sheet:
            history.append(stmt.get(key))
        return history

    def get_income_statement_history(self, key):
        history = []
        income_statement = self.module_data.get('incomeStatementHistory', {}).get('incomeStatementHistory', [])
        for stmt in income_statement:
            history.append(stmt.get(key))
        return history
