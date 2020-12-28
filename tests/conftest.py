from datetime import date, datetime
from unittest.mock import patch

import pytest
from peewee import SqliteDatabase
from tweepy import Status, User

from src.const import API_LIMIT_EXCEEDED_ERROR
from src.models import Reminder

MODELS = [Reminder]


@pytest.fixture(autouse=True)
def setup_test_db():
    test_db = SqliteDatabase(":memory:")
    test_db.bind(MODELS)
    test_db.connect()
    test_db.create_tables(MODELS)


@pytest.fixture(autouse=True)
def mock_env_variables(monkeypatch):
    monkeypatch.setenv("CONSUMER_KEY", "123")
    monkeypatch.setenv("CONSUMER_SECRET", "123")
    monkeypatch.setenv("ACCESS_TOKEN", "123")
    monkeypatch.setenv("ACCESS_TOKEN_SECRET", "123")
    monkeypatch.setenv("ALPHA_VANTAGE_API_KEY", "123")
    monkeypatch.setenv("BOT_USER_ID", "123")


@pytest.fixture(autouse=True)
def mock_tweepy():
    with patch("src.bot.init_tweepy") as mock:
        yield mock


@pytest.fixture
def twitter_user():
    user = User()
    user.screen_name = "user_name"
    return user


@pytest.fixture
def reminder():
    return Reminder.create(
        user_name="user_name",
        tweet_id=1,
        created_on=date(2020, 10, 16),
        remind_on=datetime(2021, 1, 16, 12, 0),
        stock_symbol="AMZN",
        stock_price=2954.91,
        is_finished=False,
    )


@pytest.fixture
def status(twitter_user):
    tweet = Status()
    tweet.id = 1
    tweet.text = "Price of $AMZN in 3 months."
    tweet.user = twitter_user
    return tweet


@pytest.fixture
def status_with_multiple_stocks(twitter_user):
    tweet = Status()
    tweet.id = 1
    tweet.text = "Remind me of $AMZN, $MSFT, $AAPL and $BABA in 3 months."
    tweet.user = twitter_user
    return tweet


@pytest.fixture
def mock_mention(mock_tweepy, status):
    mock_tweepy.return_value.mentions_timeline.return_value = [status]
    return mock_tweepy


@pytest.fixture
def mock_mention_with_multiple_stocks(mock_tweepy, status_with_multiple_stocks):
    mock_tweepy.return_value.mentions_timeline.return_value = [
        status_with_multiple_stocks
    ]
    return mock_tweepy


@pytest.fixture
def mock_mention_with_invalid_format(mock_tweepy, status):
    status.text = "What stocks should I buy?"
    mock_tweepy.return_value.mentions_timeline.return_value = [status]
    return mock_tweepy


@pytest.fixture
def mock_alpha_vantage_get_intraday_amazon():
    with patch("alpha_vantage.timeseries.TimeSeries.get_intraday") as mock:
        mock.return_value = (
            {
                "2020-12-13 16:55:00": {
                    "1. open": "3112.7000",
                    "2. high": "3112.7000",
                    "3. low": "3112.7000",
                    "4. close": "3112.7000",
                    "5. volume": "196",
                },
                "2020-12-13 16:50:00": {
                    "1. open": "3110.6700",
                    "2. high": "3110.6700",
                    "3. low": "3110.6700",
                    "4. close": "3110.6700",
                    "5. volume": "102",
                },
            },
            {
                "1. Information": "Intraday (15min) open, high, low, "
                "close prices and volume",
                "2. Symbol": "AMZN",
                "3. Last Refreshed": "2020-12-13 17:00:00",
                "4. Interval": "15min",
                "5. Output Size": "Compact",
                "6. Time Zone": "US/Eastern",
            },
        )
        yield mock


@pytest.fixture
def mock_alpha_vantage_get_intraday_tesla():
    with patch("alpha_vantage.timeseries.TimeSeries.get_intraday") as mock:
        mock.return_value = (
            {
                "2020-12-24 17:00:00": {
                    "1. open": "661.7000",
                    "2. high": "661.7000",
                    "3. low": "661.7000",
                    "4. close": "661.7000",
                    "5. volume": "336",
                },
                "2020-12-24 16:55:00": {
                    "1. open": "661.7000",
                    "2. high": "661.7000",
                    "3. low": "661.7000",
                    "4. close": "661.7000",
                    "5. volume": "276",
                },
            },
            {
                "1. Information": "Intraday (5min) open, high, low, "
                "close prices and volume",
                "2. Symbol": "TSLA",
                "3. Last Refreshed": "2020-12-24 17:00:00",
                "4. Interval": "5min",
                "5. Output Size": "Compact",
                "6. Time Zone": "US/Eastern",
            },
        )
        yield mock


@pytest.fixture
def mock_alpha_vantage_get_company_overview_tesla():
    with patch(
        "alpha_vantage.fundamentaldata.FundamentalData.get_company_overview"
    ) as mock:
        mock.return_value = (
            {
                "Symbol": "TSLA",
                "AssetType": "Common Stock",
                "Name": "Tesla, Inc",
                "Description": "Tesla makes fancy electric cars.",
                "Exchange": "NASDAQ",
                "MarketCapitalization": "627292438528",
                "EBITDA": "4019000064",
                "PERatio": "1265.3346",
                "PEGRatio": "1.3336",
                "DividendPerShare": "None",
                "DividendYield": "0",
                "ForwardAnnualDividendRate": "0",
                "ForwardAnnualDividendYield": "0",
                "PayoutRatio": "0",
                "DividendDate": "None",
                "ExDividendDate": "None",
                "LastSplitFactor": "5:1",
                "LastSplitDate": "2020-08-31",
            },
            None,
        )
        yield mock


@pytest.fixture
def mock_alpha_vantage_get_company_overview_amazon():
    with patch(
        "alpha_vantage.fundamentaldata.FundamentalData.get_company_overview"
    ) as mock:
        mock.return_value = (
            {
                "Symbol": "AMZN",
                "AssetType": "Common Stock",
                "Name": "Amazon.com, Inc",
                "Description": "It basically sells stuff online.",
                "Exchange": "NASDAQ",
                "MarketCapitalization": "1591900372992",
                "EBITDA": "43707998208",
                "PERatio": "92.7633",
                "PEGRatio": "1.2263",
                "DividendPerShare": "None",
                "DividendYield": "0",
                "ForwardAnnualDividendRate": "0",
                "ForwardAnnualDividendYield": "0",
                "PayoutRatio": "0",
                "DividendDate": "None",
                "ExDividendDate": "None",
                "LastSplitFactor": "2:1",
                "LastSplitDate": "1999-09-02",
            },
            None,
        )
        yield mock


@pytest.fixture
def mock_alpha_vantage_get_currency_exchange_rate():
    with patch(
        "alpha_vantage.foreignexchange.ForeignExchange.get_currency_exchange_rate"
    ) as mock:
        mock.return_value = (
            {
                "1. From_Currency Code": "BTC",
                "2. From_Currency Name": "Bitcoin",
                "3. To_Currency Code": "USD",
                "4. To_Currency Name": "United States Dollar",
                "5. Exchange Rate": "23933.49000000",
                "6. Last Refreshed": "2020-12-19 22:37:01",
                "7. Time Zone": "UTC",
                "8. Bid Price": "23930.67000000",
                "9. Ask Price": "23933.49000000",
            },
            None,
        )
        yield mock


@pytest.fixture
def mock_alpha_vantage_stock_not_found():
    with patch("alpha_vantage.timeseries.TimeSeries.get_intraday") as mock:
        mock.return_value = (
            {},
            None,
        )
        yield mock


@pytest.fixture
def mock_alpha_vantage_max_retries_exceeded():
    with patch("alpha_vantage.timeseries.TimeSeries.get_intraday") as mock:
        mock.side_effect = ValueError(API_LIMIT_EXCEEDED_ERROR)
        yield mock
