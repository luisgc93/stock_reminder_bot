from datetime import date

import pytest
from unittest.mock import call

from src import bot, const
from src.models import Mention, Reminder
from freezegun import freeze_time


class TestBot:
    @pytest.mark.usefixtures("mock_new_mention", "mock_alpha_vantage_get_intra_day")
    def test_saves_new_mentions(self, mock_tweepy):
        assert Mention.select().count() == 0

        bot.reply_to_mentions()

        mock_tweepy.assert_has_calls([call().mentions_timeline(since_id=None)])
        assert Mention.select().count() == 1

    @pytest.mark.usefixtures("mock_new_mention", "mock_alpha_vantage_get_intra_day")
    def test_creates_reminder_when_new_mention_contains_stock_and_date(self):
        assert Reminder.select().count() == 0

        with freeze_time("2020-12-13"):
            bot.reply_to_mentions()

        assert Reminder.select().count() == 1

        reminder = Reminder.select().first()
        assert reminder.tweet_id == 1
        assert reminder.created_on == date(2020, 12, 13)
        assert reminder.remind_on == date(2021, 3, 13)
        assert reminder.stock_symbol == "AMZN"
        assert reminder.stock_price == 3201.65

    @pytest.mark.usefixtures("mock_new_mention", "mock_alpha_vantage_get_intra_day")
    def test_replies_to_new_mention_when_reminder_created(self, mock_tweepy):
        with freeze_time("2020-12-13"):
            bot.reply_to_mentions()

        expected_status_call = call().update_status(
            status="@user_name Sure thing buddy! I'll remind you of the price of "
            "$AMZN on Saturday March 13 2021. I hope you make tons of money! 🤑",
            in_reply_to_status_id=1,
        )

        assert Reminder.select().count() == 1
        assert expected_status_call in mock_tweepy.mock_calls

    @pytest.mark.usefixtures("mention", "mock_alpha_vantage_get_intra_day")
    def test_replies_to_old_mention_when_reminder_date_is_today_and_stock_went_up(
        self, reminder, mock_tweepy
    ):
        with freeze_time(reminder.remind_on):
            bot.reply_to_reminders()

        expected_status_call = call().update_with_media(
            filename=const.MR_SCROOGE_IMAGE_PATH,
            status="@user_name 3 months ago you bought $AMZN at $2954.91. "
            "It is now worth $3201.65. That's a return of 8.35%! 🚀🤑📈",
            in_reply_to_status_id=1,
        )

        assert expected_status_call in mock_tweepy.mock_calls

    @pytest.mark.usefixtures("mention", "mock_alpha_vantage_get_intra_day")
    def test_replies_to_old_mention_when_reminder_date_is_today_and_stock_went_down(
        self, reminder, mock_tweepy
    ):
        reminder.stock_price = 3386.12
        reminder.save()
        with freeze_time(reminder.remind_on):
            bot.reply_to_reminders()

        expected_status_call = call().update_with_media(
            filename=const.MR_BURNS_IMAGE_PATH,
            status="@user_name 3 months ago you bought $AMZN at $3386.12. "
            "It is now worth $3201.65. That's a return of -5.45%! 😭📉",
            in_reply_to_status_id=1,
        )

        assert expected_status_call in mock_tweepy.mock_calls

    @pytest.mark.usefixtures("mention")
    def test_does_not_reply_to_old_mention_when_reminder_date_is_not_today(
        self, reminder, mock_tweepy
    ):
        with freeze_time("2020-12-14"):
            bot.reply_to_reminders()

        mock_tweepy.assert_not_called()

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
        "tweet, stock_name",
        [
            ("What is the price of $AMZN?", "AMZN"),
            ("How much is $WMT right now?", "WMT"),
        ],
    )
    def test_returns_stock_name_when_tweet_contains_cash_tag(self, tweet, stock_name):
        assert bot.parse_stock_symbol(tweet) == stock_name

    def test_returns_price_for_stock(self, mock_alpha_vantage_get_intra_day):
        price = bot.get_price("AMZN")

        assert price == 3201.65
        mock_alpha_vantage_get_intra_day.assert_called_once_with("AMZN")

    def test_returns_price_for_cryptocurrency(
        self, mock_alpha_vantage_get_currency_exchange_rate
    ):
        price = bot.get_price("BTC")

        assert price == 23933.49
        mock_alpha_vantage_get_currency_exchange_rate.assert_called_once_with(
            "BTC", "USD"
        )

    @pytest.mark.parametrize(
        "string, reminder_date",
        [
            ("Remind me of this tomorrow", date(2020, 12, 14)),
            ("Remind me of $AMZ in 3 days", date(2020, 12, 16)),
            ("in one week", date(2020, 12, 20)),
            ("in two months", date(2021, 2, 13)),
            ("$MSFT in 2 years", date(2022, 12, 13)),
        ],
    )
    def test_calculates_reminder_date_from_string(self, string, reminder_date):
        with freeze_time("2020-12-13"):
            assert bot.calculate_reminder_date(string) == reminder_date
