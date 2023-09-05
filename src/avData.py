from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
import math


class avData:
    def __init__(self, ticker_symbol, token):
        self.ticker = ticker_symbol.replace('.', '-')
        self.token = token

    def get_stock_data_from_alpha_vantage(self):
        timeseries = TimeSeries(key=self.token, output_format='pandas')
        fundamental = FundamentalData(key=self.token, output_format='pandas')

        # Fetch data from the daily endpoint for volume data
        daily_data, _ = timeseries.get_daily(symbol=self.ticker, outputsize='full')
        today_data = daily_data.iloc[0]
        three_months_data = daily_data.head(60)  # Approximation, considering average month has 20 trading days
        ten_days_data = daily_data.head(10)

        # Fetch data for key statistics
        overview, _ = fundamental.get_company_overview(symbol=self.ticker)

        # Fetch earnings per share from income statement
        income_statement, _ = fundamental.get_income_statement_annual(symbol=self.ticker)
        recent_year_eps = income_statement['reportedEPS'].iloc[0]
        previous_year_eps = income_statement['reportedEPS'].iloc[1]
        ttm_eps = recent_year_eps - previous_year_eps

        data = {
            "name": overview['Name'][0],
            "average_volume": self.calculate_average_volume(today_data['5. volume'], three_months_data['5. volume'].mean(),
                                                            ten_days_data['5. volume'].mean()),
            "current_price": today_data['4. close'],
            "market_cap": float(overview['MarketCapitalization']),
            "ttm_eps": ttm_eps,
            "five_year_growth_rate": self.calculate_five_year_growth_rate(daily_data)
        }

        return data

    def calculate_five_year_growth_rate(self, daily_data):
        beginning_price = daily_data.iloc[-(5 * 252)]['4. close']  # 252 trading days in a year
        ending_price = daily_data.iloc[0]['4. close']

        years = 5
        cagr = ((ending_price / beginning_price) ** (1 / years)) - 1

        return cagr

    def calculate_average_volume(self, regularMarketVolume, averageDailyVolume3Month, averageDailyVolume10Day):
        return max(0, min(regularMarketVolume, averageDailyVolume3Month, averageDailyVolume10Day))
