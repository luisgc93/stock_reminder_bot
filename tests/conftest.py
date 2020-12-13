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
def status(twitter_user):
    tweet = Status()
    tweet.id = 1
    tweet.text = "Price of $BABA in 3 months."
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
                "2020-11-27 16:55:00": {
                    "1. open": "276.8000",
                    "2. high": "276.8000",
                    "3. low": "276.8000",
                    "4. close": "276.8000",
                    "5. volume": "513",
                },
                "2020-11-27 16:50:00": {
                    "1. open": "276.9000",
                    "2. high": "276.9800",
                    "3. low": "276.8400",
                    "4. close": "276.9800",
                    "5. volume": "754",
                },
            },
            {
                "1. Information": "Intraday (15min) open, high, low, "
                "close prices and volume",
                "2. Symbol": "BABA",
                "3. Last Refreshed": "2020-11-27 17:00:00",
                "4. Interval": "15min",
                "5. Output Size": "Compact",
                "6. Time Zone": "US/Eastern",
            },
        )
        yield mock
