from datetime import datetime, date

import pytest
from unittest.mock import call

import pytz

from src import bot
from src.models import Mention, Reminder
from freezegun import freeze_time


class TestBot:
    @pytest.mark.usefixtures("mock_new_mention")
    def test_saves_new_mentions(self, mock_tweepy):
        assert Mention.select().count() == 0

        bot.reply_to_mentions()

        mock_tweepy.assert_has_calls([call().mentions_timeline(since_id=None)])
        assert Mention.select().count() == 1

    @pytest.mark.usefixtures("mock_new_mention")
    def test_saves_reminder_when_new_mention_contains_stock_and_date(self):
        assert Reminder.select().count() == 0

        bot.reply_to_mentions()

        assert Reminder.select().count() == 1


class TestParseTweet:
    def test_returns_true_when_tweet_contains_cash_tag(self):

        assert bot.contains_stock("What is the price of $AMZN?") is True

    def test_returns_false_when_tweet_does_not_contain_cash_tag(self):

        assert bot.contains_stock("What is the price of amazon?") is False

    def test_returns_true_when_tweet_contains_date(self):

        assert bot.contains_date("Remind me of $BABA in one year") is True

    def test_returns_false_when_tweet_does_not_contain_date(self):

        assert bot.contains_date("Hello there!") is False

    @pytest.mark.parametrize(
        "tweet, stock_name",
        [
            ("What is the price of $AMZN?", "AMZN"),
            ("How much is $WMT right now?", "WMT"),
        ],
    )
    def test_returns_stock_name_when_tweet_contains_cash_tag(self, tweet, stock_name):
        assert bot.parse_stock_name(tweet) == stock_name

    @pytest.mark.usefixtures("mock_alpha_vantage_get_intra_day")
    def test_returns_stock_price_with_two_decimal_places(self):
        price = bot.get_stock_price("BABA")

        assert price == "$276.80"

    @pytest.mark.parametrize(
        "string, reminder_date",
        [
            ("in 3 days", datetime(2020, 12, 16, 11, tzinfo=pytz.utc)),
            ("in one week", datetime(2020, 12, 20, 11, tzinfo=pytz.utc)),
            ("in two months", datetime(2021, 2, 13, 11, tzinfo=pytz.utc)),
            ("in 2 years", datetime(2022, 12, 13, 11, tzinfo=pytz.utc)),
        ],
    )
    def test_calculates_reminder_date_from_string(self, string, reminder_date):
        published_at = datetime(2020, 12, 13, 11, tzinfo=pytz.utc)
        with freeze_time(published_at):
            assert bot.calculate_reminder_date(string).date() == reminder_date.date()
