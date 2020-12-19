from datetime import date
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
        user_name="user_name",
        tweet_id=mention.id,
        created_on=date(2020, 10, 16),
        remind_on=date(2021, 1, 16),
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
    with patch("alpha_vantage.timeseries.TimeSeries.get_quote_endpoint") as mock:
        mock.return_value = [
            {
                "01. symbol": "AMZN",
                "02. open": "3243.9900",
                "03. high": "3249.4200",
                "04. low": "3171.6000",
                "05. price": "3201.6500",
                "06. volume": "5995713",
                "07. latest trading day": "2020-12-18",
                "08. previous close": "3236.0800",
                "09. change": "-34.4300",
                "10. change percent": "-1.0639%",
            },
            None,
        ]
        yield mock
