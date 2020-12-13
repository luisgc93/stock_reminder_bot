from datetime import datetime

import pytest
from unittest.mock import call

import pytz

from src import bot
from src.models import Mention
from freezegun import freeze_time


class TestBot:
    @pytest.mark.usefixtures("mock_new_mention")
    def test_saves_new_mentions(self, mock_tweepy):
        assert Mention.select().count() == 0

        bot.reply_to_mentions()

        mock_tweepy.assert_has_calls([call().mentions_timeline(since_id=None)])
        assert Mention.select().count() == 1


class TestParseTweet:
    def test_returns_true_when_tweet_contains_cash_tag(self):

        assert bot.tweet_contains_stock("What is the price of $AMZN?") is True

    def test_returns_false_when_tweet_does_not_contain_cash_tag(self):

        assert bot.tweet_contains_stock("What is the price of amazon?") is False

    def test_returns_true_when_tweet_contains_date(self):

        assert bot.tweet_contains_date("Remind me of $BABA in one year") is True

    def test_returns_false_when_tweet_does_not_contain_date(self):

        assert bot.tweet_contains_date("Hello there!") is False

    @pytest.mark.parametrize(
        "tweet, stock_name",
        [
            ("What is the price of $AMZN?", "AMZN"),
            ("How much is $WMT right now?", "WMT"),
        ],
    )
    def test_returns_stock_name_when_tweet_contains_cash_tag(self, tweet, stock_name):
        assert bot.parse_stock_name(tweet) == stock_name

    def test_returns_reminder_date_from_string(self):
        with freeze_time("2020-12-13T11:00+01:00"):
            assert bot.parse_reminder_date("in one week") == datetime(
                2020, 12, 20, 11, 0, tzinfo=pytz.utc
            )
