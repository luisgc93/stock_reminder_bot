from datetime import datetime
from unittest.mock import patch

import pytest
from peewee import SqliteDatabase
from tweepy import Status, User

from src.models import Mention, Reminder

MODELS = [Mention, Reminder]


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
def mention():
    return Mention.create(tweet_id=1)


@pytest.fixture
def reminder(mention):
    return Reminder.create(
        tweet_id=mention.id,
        created_on=datetime(2020, 12, 13),
        remind_on=datetime(2021, 12, 13),
        stock_symbol="AMZN",
        stock_price=2954.91,
    )


@pytest.fixture
def status(twitter_user):
    tweet = Status()
    tweet.id = 1
    tweet.text = "Price of $AMZN in 3 months."
    tweet.user = twitter_user
    return tweet


@pytest.fixture
def mock_new_mention(mock_tweepy, status):
    mock_tweepy.return_value.mentions_timeline.return_value = [status]
    return mock_tweepy


@pytest.fixture
def mock_alpha_vantage_get_intra_day():
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
