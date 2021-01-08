from datetime import date, datetime
from unittest.mock import patch, Mock

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
    monkeypatch.setenv("GIPHY_API_KEY", "123")
    monkeypatch.setenv("FMP_API_KEY", "123")
    monkeypatch.setenv("SAVE_RATINGS_IMG", "123")


@pytest.fixture(autouse=True)
def mock_tweepy():
    with patch("src.bot.init_tweepy") as mock:
        yield mock


@pytest.fixture(autouse=True)
def mock_giphy():
    with patch("src.bot.download_random_gif") as mock:
        yield mock


@pytest.fixture
def mock_fmp_api_rating_response():
    with patch("requests.get") as mock:
        json_response = {
            "symbol": "AMZN",
            "rating": {"score": 4, "rating": "A+", "recommendation": "Buy"},
            "ratingDetails": {
                "P/B": {"score": 5, "recommendation": "Strong Buy"},
                "ROA": {"score": 4, "recommendation": "Neutral"},
                "DCF": {"score": 3, "recommendation": "Neutral"},
                "P/E": {"score": 5, "recommendation": "Strong Buy"},
                "ROE": {"score": 4, "recommendation": "Buy"},
                "D/E": {"score": 3, "recommendation": "Buy"},
            },
        }
        mock.return_value = Mock()
        mock.return_value.json.return_value = json_response
        yield mock


@pytest.fixture
def mock_fmp_api_get_price_response():
    with patch("requests.get") as mock:
        json_response = [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "price": 126.66,
                "dayLow": 126.382,
                "dayHigh": 131.0499,
                "yearHigh": 138.79,
                "yearLow": 53.1525,
                "volume": 155087970,
                "exchange": "NASDAQ",
                "open": 127.72,
                "previousClose": 131.01,
            }
        ]

        mock.return_value = Mock()
        mock.return_value.json.return_value = json_response
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
        created_on=date(2020, 10, 15),
        remind_on=datetime(2021, 1, 15, 16, 52),
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
def mock_mention(mock_tweepy, status):
    mock_tweepy.return_value.mentions_timeline.return_value = [status]
    return mock_tweepy


@pytest.fixture
def mock_mention_with_multiple_stocks(mock_tweepy, status):
    status.text = "Remind me of $AMZN, $MSFT, $AAPL and $BABA in 3 months."
    mock_tweepy.return_value.mentions_timeline.return_value = [status]
    return mock_tweepy


@pytest.fixture
def mock_mention_for_stock_shorting(mock_tweepy, status):
    status.text = "Short $BTC remind me in 1 months."
    mock_tweepy.return_value.mentions_timeline.return_value = [status]
    return mock_tweepy


@pytest.fixture
def mock_mention_asking_for_report(mock_tweepy, status):
    status.text = "Report for $AMZN"
    mock_tweepy.return_value.mentions_timeline.return_value = [status]
    return mock_tweepy


@pytest.fixture
def mock_mention_asking_for_crypto_report(mock_tweepy, status):
    status.text = "Report for $ETH"
    mock_tweepy.return_value.mentions_timeline.return_value = [status]
    return mock_tweepy


@pytest.fixture
def mock_mention_with_invalid_format(mock_tweepy, status):
    status.text = "What stocks should I buy?"
    mock_tweepy.return_value.mentions_timeline.return_value = [status]
    return mock_tweepy


@pytest.fixture
def mock_alpha_vantage_get_quote_amazon():
    with patch("alpha_vantage.timeseries.TimeSeries.get_quote_endpoint") as mock:
        mock.return_value = {
            "01. symbol": "AMZN",
            "02. open": "3146.4800",
            "03. high": "3197.5090",
            "04. low": "3131.1600",
            "05. price": "3138.3800",
            "06. volume": "4394815",
            "07. latest trading day": "1999-01-06",
            "08. previous close": "3218.5100",
            "09. change": "-80.1300",
            "10. change percent": "-2.4897%",
        }
        yield mock


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
def mock_alpha_vantage_get_intraday_jnj():
    with patch("alpha_vantage.timeseries.TimeSeries.get_intraday") as mock:
        mock.return_value = (
            {
                "2020-12-31 19:35:00": {
                    "1. open": "157.1100",
                    "2. high": "157.1100",
                    "3. low": "157.1100",
                    "4. close": "157.1100",
                    "5. volume": "100",
                },
                "2020-12-31 19:30:00": {
                    "1. open": "157.5000",
                    "2. high": "157.5000",
                    "3. low": "157.5000",
                    "4. close": "157.5000",
                    "5. volume": "400",
                },
            },
            {
                "1. Information": "Intraday (5min) open, high, low, "
                "close prices and volume",
                "2. Symbol": "JNJ",
                "3. Last Refreshed": "2020-12-31 17:00:00",
                "4. Interval": "5min",
                "5. Output Size": "Compact",
                "6. Time Zone": "US/Eastern",
            },
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
def mock_alpha_vantage_get_company_overview_jnj():
    with patch(
        "alpha_vantage.fundamentaldata.FundamentalData.get_company_overview"
    ) as mock:
        mock.return_value = (
            {
                "Symbol": "JNJ",
                "AssetType": "Common Stock",
                "Name": "Johnson & Johnson",
                "Description": "Johnson & Johnson makes top-notch shampoos",
                "Exchange": "NASDAQ",
                "MarketCapitalization": "414309154816",
                "EBITDA": "27264000000",
                "PERatio": "24.7453",
                "PEGRatio": "2.8436",
                "DividendPerShare": "4.04",
                "DividendYield": "0.0257",
                "ForwardAnnualDividendRate": "4.04",
                "ForwardAnnualDividendYield": "0.0257",
                "PayoutRatio": "0.4944",
                "DividendDate": "2020-12-08",
                "ExDividendDate": "2020-11-23",
                "LastSplitFactor": "2:1",
                "LastSplitDate": "2001-06-13",
            },
            None,
        )
        yield mock


@pytest.fixture
def mock_alpha_vantage_get_daily_adjusted_amazon():
    with patch("alpha_vantage.timeseries.TimeSeries.get_daily_adjusted") as mock:
        mock.return_value = (
            {
                "2020-12-31": {
                    "1. open": "3275.0",
                    "2. high": "3282.9219",
                    "3. low": "3241.2",
                    "4. close": "3256.93",
                    "5. adjusted close": "3256.93",
                    "6. volume": "2957206",
                    "7. dividend amount": "0.0000",
                    "8. split coefficient": "1.0",
                },
                "2020-12-30": {
                    "1. open": "3341.0",
                    "2. high": "3342.1",
                    "3. low": "3282.47",
                    "4. close": "3285.85",
                    "5. adjusted close": "3285.85",
                    "6. volume": "3209310",
                    "7. dividend amount": "0.0000",
                    "8. split coefficient": "1.0",
                },
            },
            {
                "1. Information": "Daily Time Series with Splits and Dividend Events",
                "2. Symbol": "AMZN",
                "3. Last Refreshed": "2020-12-31",
                "4. Output Size": "Compact",
                "5. Time Zone": "US/Eastern",
            },
        )

        yield mock


@pytest.fixture
def mock_alpha_vantage_get_daily_adjusted_tesla():
    with patch("alpha_vantage.timeseries.TimeSeries.get_daily_adjusted") as mock:
        mock.return_value = (
            {
                "2020-12-31": {
                    "1. open": "699.99",
                    "2. high": "718.72",
                    "3. low": "691.12",
                    "4. close": "705.67",
                    "5. adjusted close": "705.67",
                    "6. volume": "49649928",
                    "7. dividend amount": "0.0000",
                    "8. split coefficient": "1.0",
                },
                "2020-12-30": {
                    "1. open": "672.0",
                    "2. high": "696.6",
                    "3. low": "668.3603",
                    "4. close": "694.78",
                    "5. adjusted close": "694.78",
                    "6. volume": "42846021",
                    "7. dividend amount": "0.0000",
                    "8. split coefficient": "1.0",
                },
            },
            {
                "1. Information": "Daily Time Series with Splits and Dividend Events",
                "2. Symbol": "TSLA",
                "3. Last Refreshed": "2020-12-31",
                "4. Output Size": "Compact",
                "5. Time Zone": "US/Eastern",
            },
        )

        yield mock


@pytest.fixture
def mock_alpha_vantage_get_daily_adjusted_jnj():
    with patch("alpha_vantage.timeseries.TimeSeries.get_daily_adjusted") as mock:
        mock.return_value = (
            {
                "2020-12-31": {
                    "1. open": "156.53",
                    "2. high": "157.66",
                    "3. low": "155.1098",
                    "4. close": "157.38",
                    "5. adjusted close": "157.38",
                    "6. volume": "5099880",
                    "7. dividend amount": "0.0000",
                    "8. split coefficient": "1.0",
                },
                "2020-12-30": {
                    "1. open": "154.74",
                    "2. high": "156.38",
                    "3. low": "154.6",
                    "4. close": "156.05",
                    "5. adjusted close": "156.05",
                    "6. volume": "5412775",
                    "7. dividend amount": "1.0100",
                    "8. split coefficient": "1.0",
                },
            },
            {
                "1. Information": "Daily Time Series with Splits and Dividend Events",
                "2. Symbol": "JNJ",
                "3. Last Refreshed": "2020-12-31",
                "4. Output Size": "Compact",
                "5. Time Zone": "US/Eastern",
            },
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
def mock_alpha_vantage_crypto_rating():
    with patch(
        "alpha_vantage.cryptocurrencies.CryptoCurrencies.get_digital_crypto_rating"
    ) as mock:
        mock.return_value = (
            {
                "1. symbol": "ETH",
                "2. name": "Ethereum",
                "3. fcas rating": "Superb",
                "4. fcas score": "970",
                "5. developer score": "965",
                "6. market maturity score": "876",
                "7. utility score": "996",
                "8. last refreshed": "2021-01-05 00:00:00",
                "9. timezone": "UTC",
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
