from datetime import datetime, time, date
from os import environ

import humanize
import pytz
import requests
from alpha_vantage.foreignexchange import ForeignExchange
from alpha_vantage.fundamentaldata import FundamentalData
from alpha_vantage.timeseries import TimeSeries

import const


class FinancialApiClient:
    def __init__(self, currencies: ForeignExchange, stocks: TimeSeries, analysis: FundamentalData):
        self.stocks = stocks
        self.currencies = currencies
        self.analysis = analysis

    def get_price(self, ticker) -> float:
        if ticker in const.CRYPTO_CURRENCIES:
            data, _ = self.currencies.get_currency_exchange_rate(ticker, "USD")
            full_price = data["5. Exchange Rate"]
            return float(full_price[:-2])
        else:
            try:
                if self.is_nasdaq_open():
                    data, meta_data = self.stocks.get_intraday(ticker)
                    key = list(data.keys())[0]
                    full_price = data[key]["4. close"]
                    return float(full_price[:-2])
                else:
                    data, _ = self.stocks.get_quote_endpoint(ticker)
                    full_price = data["05. price"]
                    return float(full_price[:-2])
            except ValueError:
                response = requests.get(
                    f"{const.FMP_API_GET_PRICE_ENDPOINT}"
                    f'{ticker}?apikey={environ["FMP_API_KEY"]}'
                )
                return response.json()[0]["price"]

    def is_nasdaq_open(self) -> bool:
        nyc_now = datetime.now(pytz.timezone("US/Eastern"))
        if nyc_now.weekday() in const.WEEKEND_DAYS:
            return False
        nyc_time = nyc_now.time()
        open_time = time(hour=9, minute=30)
        closing_time = time(hour=16, minute=00)
        return closing_time >= nyc_time >= open_time

    def get_split_factor(self, ticker, purchase_date) -> float:
        if ticker in const.CRYPTO_CURRENCIES:
            return 1.0

        data, _ = self.analysis.get_company_overview(ticker)

        if data["LastSplitDate"] == "None":
            return 1.0
        split_date = datetime.strptime(data["LastSplitDate"], "%Y-%m-%d").date()
        stock_was_split = purchase_date < split_date <= date.today()
        if stock_was_split:
            return float(data["LastSplitFactor"][0]) / float(data["LastSplitFactor"][2])
        return 1.0

    def get_dividend(self, ticker, purchase_date) -> float:
        """
        Calculate the stock's total dividend payout from the purchase date to the current date
        :param ticker:
        :param purchase_date:
        :return:
        """

        if ticker in const.CRYPTO_CURRENCIES:
            return 0.0

        delta = datetime.today() - purchase_date
        if delta.days > 90:
            outputsize = "full"
        else:
            outputsize = "compact"
        data, _ = self.stocks.get_daily_adjusted(ticker, outputsize=outputsize)
        keys = list(data.keys())
        dividend = 0.0
        for key in keys:
            dividend_date = datetime.strptime(key, "%Y-%m-%d").date()
            if purchase_date < dividend_date <= datetime.today():
                dividend += float(data[key]["7. dividend amount"])

        return dividend

    def generate_investment_results(self, reminder):
        split_factor = self.get_split_factor(reminder.stock_symbol, reminder.created_on)
        dividend = self.get_dividend(reminder)
        original_adjusted_price = reminder.stock_price / split_factor
        current_price = self.get_price(reminder.stock_symbol)
        rate_of_return = self._calculate_returns(original_adjusted_price, current_price, dividend)
        stock_split_message = "."
        dividend_message = ""
        if split_factor != 1.0:
            stock_split_message = (
                f" (${'{:,.2f}'.format(original_adjusted_price)} "
                f"after adjusting for the stock split)."
            )
        if dividend:
            dividend_message = (
                f" and a total dividend of ${'{:.2f}'.format(dividend)} was paid out"
            )
        time_since_created_on = self._calculate_time_delta(date.today(), reminder.created_on)
        user_action = "bought"
        if reminder.short:
            rate_of_return *= -1
            user_action = "shorted"

        emoji = const.POSITIVE_RETURNS_EMOJI
        if rate_of_return == 0:
            emoji = const.ZERO_RETURNS_EMOJI
        if rate_of_return < 0:
            emoji = const.NEGATIVE_RETURNS_EMOJI

        return (
            f"@{reminder.user_name} {time_since_created_on} ago you {user_action} "
            f"${reminder.stock_symbol} at ${'{:,.2f}'.format(reminder.stock_price)}"
            f"{stock_split_message} It is now worth ${'{:,.2f}'.format(current_price)}"
            f"{dividend_message}. That's a return of {rate_of_return}%! {emoji}"
        )

    def generate_rating(self, stock):
        rating_response = requests.get(
            f'{const.FMP_API_RATING_ENDPOINT}{stock}?apikey={environ["FMP_API_KEY"]}'
        )
        rating_data = rating_response.json()

        if not rating_data:
            return ": "

        ratings_list = [
            (key.capitalize() + ": " + str(value))
            for key, value in rating_data["rating"].items()
        ]

        return ". " + ", ".join(ratings_list) + ". Details: "

    def _calculate_returns(self, original_price, current_price, dividend):
        return round(
            ((current_price - original_price + dividend) / original_price) * 100, 2
        )

    def _calculate_time_delta(self, today, created_on):
        # THESE HELPER METHODS DON'T USE ANY INSTANCE DATA
        # MIGHT BE A BETTER IDEA TO PLACE THEM IN A HELPER MODULE
        return humanize.naturaldelta(today - created_on)