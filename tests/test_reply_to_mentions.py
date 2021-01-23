from datetime import date

import pytest
from unittest.mock import call

from src import bot, const
from src.models import Reminder
from freezegun import freeze_time


@freeze_time("2020-12-11T15:32:00Z")
class TestReplyToMentions:
    @pytest.mark.usefixtures("mock_mention")
    def test_creates_reminder_when_mention_contains_stock_and_date(
        self, mock_alpha_vantage_get_intraday_amazon
    ):
        assert Reminder.select().count() == 0

        bot.reply_to_mentions()

        assert Reminder.select().count() == 1

        reminder = Reminder.select().first()
        assert reminder.tweet_id == 1
        assert reminder.created_on == date(2020, 12, 11)
        assert reminder.remind_on == "2021-03-11 15:32:00+00:00"
        assert reminder.stock_symbol == "AMZN"
        assert reminder.stock_price == 3112.70
        assert reminder.is_finished is False
        assert reminder.short is False
        mock_alpha_vantage_get_intraday_amazon.assert_called_once_with("AMZN")

    @pytest.mark.usefixtures(
        "mock_mention_with_multiple_stocks", "mock_alpha_vantage_get_intraday_amazon"
    )
    def test_creates_reminders_when_mention_contains_multiple_stocks_and_date(
        self,
    ):
        assert Reminder.select().count() == 0

        bot.reply_to_mentions()

        reminders = Reminder.select()
        assert reminders.count() == 4
        assert [reminder.stock_symbol for reminder in reminders] == [
            "AMZN",
            "MSFT",
            "AAPL",
            "BABA",
        ]

    @pytest.mark.usefixtures(
        "mock_mention_for_stock_shorting", "mock_alpha_vantage_get_intraday_amazon"
    )
    def test_creates_reminder_for_stock_shorting(self):
        assert Reminder.select().count() == 0

        bot.reply_to_mentions()

        reminder = Reminder.select().first()
        assert reminder.short is True

    @pytest.mark.usefixtures("mock_mention_replies_to_another_tweet")
    def test_creates_reminder_when_mention_is_a_reply_to_another_tweet(
        self, mock_alpha_vantage_get_intraday_amazon
    ):
        bot.reply_to_mentions()

        mock_alpha_vantage_get_intraday_amazon.assert_called_once_with("AMZN")
        assert Reminder.select().count() == 1
        assert Reminder.select().first().tweet_id == 2

    @pytest.mark.usefixtures(
        "mock_mention_replies_to_another_tweet",
        "mock_alpha_vantage_get_intraday_amazon",
    )
    def test_replies_to_mention_when_mention_is_a_reply_to_another_tweet(
        self, mock_tweepy, mock_giphy
    ):
        bot.reply_to_mentions()

        expected_calls = [
            call().update_status(
                status="@user_name Sure thing buddy! I'll remind you of the price of "
                "$AMZN on Saturday December 11 2021. I hope you make tons of money! 🤑",
                in_reply_to_status_id=2,
            ),
        ]

        assert expected_calls in mock_tweepy.mock_calls

    @pytest.mark.usefixtures("mock_mention", "mock_alpha_vantage_get_intraday_amazon")
    def test_replies_to_mention_when_reminder_created(self, mock_tweepy, mock_giphy):
        bot.reply_to_mentions()

        expected_calls = [
            call().update_status(
                status="@user_name Sure thing buddy! I'll remind you of the price of "
                "$AMZN on Thursday March 11 2021. I hope you make tons of money! 🤑",
                in_reply_to_status_id=1,
            ),
        ]

        assert Reminder.select().count() == 1
        assert expected_calls in mock_tweepy.mock_calls

    @pytest.mark.usefixtures(
        "mock_mention_with_multiple_stocks", "mock_alpha_vantage_get_intraday_amazon"
    )
    def test_replies_when_multiple_reminders_created(self, mock_tweepy, mock_giphy):
        bot.reply_to_mentions()

        expected_calls = [
            call().update_status(
                status="@user_name Sure thing buddy! I'll remind you of the price of "
                "$AMZN, $MSFT, $AAPL and $BABA on Thursday March 11 2021. I hope you "
                "make tons of money! 🤑",
                in_reply_to_status_id=1,
            ),
        ]

        assert Reminder.select().count() == 4
        assert expected_calls in mock_tweepy.mock_calls

    @pytest.mark.usefixtures("mock_mention_with_invalid_format")
    def test_replies_with_help_message_when_mention_is_not_valid(self, mock_tweepy):
        bot.reply_to_mentions()

        expected_status_call = call().update_status(
            status="@user_name To create a reminder, mention me "
            "with one or more ticker symbols and a date. "
            "E.g. 'Remind me of $BTC in 3 months'. "
            "You can read about all my other features and "
            "implementation at: http://cutt.ly/Rh8CoJt",
            in_reply_to_status_id=1,
        )

        assert expected_status_call in mock_tweepy.mock_calls
        assert Reminder.select().count() == 0

    @pytest.mark.usefixtures("mock_mention", "mock_alpha_vantage_stock_not_found")
    def test_replies_when_stock_is_not_found(self, mock_tweepy):
        bot.reply_to_mentions()

        expected_status_call = call().update_status(
            status=f"@user_name {const.STOCK_NOT_FOUND_RESPONSE}",
            in_reply_to_status_id=1,
        )

        assert expected_status_call in mock_tweepy.mock_calls
