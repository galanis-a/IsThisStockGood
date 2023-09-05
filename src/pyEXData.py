import pyEX as p


class pyEXData:
    def __init__(self, ticker_symbol, token):
        self.ticker = ticker_symbol.replace('.', '-')
        self.token = token

    def get_stock_data_from_pyex(self):
        client = p.Client(api_token=self.token, version='stable')

        # Fetch data from the quote endpoint
        quote_data = client.quote(self.ticker)

        # Fetch data from the stats endpoint
        stats_data = client.keyStats(self.ticker)

        # Extracting data from fetched results
        data = {
            "name": quote_data.companyName,
            "average_volume": self.calculate_average_volume(quote_data, stats_data),
            "current_price": quote_data.latestPrice,
            "market_cap": quote_data.marketCap,
            "ttm_eps": stats_data.ttmEPS,
            "five_year_growth_rate": self.calculate_five_year_growth_rate()
        }

        return data

    def calculate_five_year_growth_rate(self):
        client = p.Client(api_token=self.token, version='stable')

        # Fetch historical data
        historical_data = client.chartDF(self.ticker, timeframe='5y')

        # Extract beginning and ending prices
        beginning_price = historical_data.iloc[0]['close']
        ending_price = historical_data.iloc[-1]['close']

        # Calculate the CAGR
        years = 5
        cagr = ((ending_price / beginning_price) ** (1 / years)) - 1

        return cagr

    def calculate_average_volume(self, quote_data, stats_data):
        return max(0, min(quote_data.latestVolume, stats_data.avg30Volume, stats_data.avg10Volume))
