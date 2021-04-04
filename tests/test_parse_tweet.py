from datetime import date, datetime

import pytest

import pytz

from src import bot
from freezegun import freeze_time


class TestParseTweet:
    def test_returns_true_when_tweet_contains_cash_tag(self):

        assert bot.contains_stock("What is the price of $AMZN?") is True

    def test_returns_false_when_tweet_does_not_contain_cash_tag(self):

        assert bot.contains_stock("What is the price of amazon?") is False

    @pytest.mark.parametrize(
        "date_string",
        ["tomorrow", "3 days", "2 months", "1 year", "one week", "two years"],
    )
    def test_returns_true_when_tweet_contains_date(self, date_string):

        assert bot.contains_date(f"Remind me of $AMZN in {date_string}") is True

    def test_returns_false_when_tweet_does_not_contain_date(self):

        assert bot.contains_date("Hello there!") is False

    @pytest.mark.parametrize(
        "tweet, stock_tickers",
        [
            ("$AMZN in 7 months", ["$AMZN"]),
            ("$msft 1/28/2021", ["$msft"]),
            (
                "Remind me next year of: $VEEV $ABBV $DOCU $ADYEN $GOOG $IRM $DLR",
                ["$VEEV", "$ABBV", "$DOCU", "$ADYEN", "$GOOG", "$IRM", "$DLR"],
            ),
            (
                "Remind me of $AMZN, $AAPL and $BABA in 3 months.",
                ["$AMZN", "$AAPL", "$BABA"],
            ),
            ("$DDOG and $SNOW in 6 months", ["$DDOG", "$SNOW"]),
            ("$TSLA is a great buy at $660", ["$TSLA"]),
        ],
    )
    def test_returns_stock_tickers_when_tweet_contains_stocks(
        self, tweet, stock_tickers
    ):

        assert bot.parse_stock_symbols(tweet) == stock_tickers

    @pytest.mark.parametrize(
        "string, reminder_date",
        [
            ("tomorrow", datetime(2020, 12, 14, 9, 0, tzinfo=pytz.utc)),
            ("In 3 days", datetime(2020, 12, 16, 15, 32, tzinfo=pytz.utc)),
            ("in one week", datetime(2020, 12, 20, 15, 32, tzinfo=pytz.utc)),
            ("in a month", datetime(2021, 1, 13, 15, 32, tzinfo=pytz.utc)),
            ("in two months", datetime(2021, 2, 13, 15, 32, tzinfo=pytz.utc)),
            ("$MSFT in 2 years", datetime(2022, 12, 13, 15, 32, tzinfo=pytz.utc)),
            ("$BTC in 1 hour", datetime(2020, 12, 13, 16, 32, tzinfo=pytz.utc)),
            ("$BTC in 2 hours", datetime(2020, 12, 13, 17, 32, tzinfo=pytz.utc)),
            ("$BTC in 20 minutes", datetime(2020, 12, 13, 15, 52, tzinfo=pytz.utc)),
        ],
    )
    def test_calculates_reminder_date_from_string(self, string, reminder_date):
        with freeze_time("2020-12-13T15:32:00Z"):
            assert bot.calculate_reminder_date(string) == reminder_date

    @pytest.mark.parametrize(
        "today, created_on, delta",
        [
            (date(2021, 1, 16), date(2020, 10, 16), "3 months"),
            (date(2020, 10, 30), date(2020, 10, 16), "14 days"),
            (date(2020, 11, 16), date(2020, 5, 16), "6 months"),
            (date(2020, 1, 16), date(2019, 1, 16), "a year"),
        ],
    )
    def test_calculates_time_delta(self, today, created_on, delta):
        assert bot.calculate_time_delta(today, created_on) == delta
