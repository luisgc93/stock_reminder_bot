from datetime import date, datetime

import pytest
from unittest.mock import call, ANY

from src import bot, const
from freezegun import freeze_time


class TestPublishReminders:
    @pytest.mark.usefixtures(
        "mock_alpha_vantage_get_intraday",
        "mock_alpha_vantage_get_company_overview_amazon",
        "mock_alpha_vantage_get_daily_adjusted_amazon",
    )
    def test_publishes_reminder_when_remind_on_is_today_and_stock_went_up(
        self, reminder, mock_tweepy, mock_giphy
    ):
        with freeze_time(reminder.remind_on):
            bot.publish_reminders()

        expected_calls = [
            call().media_upload("random.gif"),
            call().update_status(
                status="@user_name 3 months ago you bought $AMZN at $2,954.91. "
                "It is now worth $3,112.70. That's a return of 5.34%! 🚀🤑📈",
                media_ids=[ANY],
                in_reply_to_status_id=1,
            ),
        ]

        mock_giphy.assert_called_once_with(const.POSITIVE_RETURN_TAGS)
        assert expected_calls in mock_tweepy.mock_calls
        assert reminder.refresh_from_db().is_finished is True

    @pytest.mark.usefixtures(
        "mock_alpha_vantage_get_intraday",
        "mock_alpha_vantage_get_company_overview_amazon",
        "mock_alpha_vantage_get_daily_adjusted_amazon",
    )
    def test_publishes_reminder_when_remind_on_is_today_and_stock_went_down(
        self, reminder, mock_tweepy, mock_download_negative_returns_gif
    ):
        reminder.stock_price = 3386.12
        reminder.save()
        with freeze_time(reminder.remind_on):
            bot.publish_reminders()

        expected_calls = [
            call().media_upload("random.gif"),
            call().update_status(
                status="@user_name 3 months ago you bought $AMZN at $3,386.12. "
                "It is now worth $3,112.70. That's a return of -8.07%! 😭📉",
                media_ids=[ANY],
                in_reply_to_status_id=1,
            ),
        ]

        mock_download_negative_returns_gif.assert_called_once()
        assert expected_calls in mock_tweepy.mock_calls
        assert reminder.refresh_from_db().is_finished is True

    @pytest.mark.usefixtures(
        "mock_alpha_vantage_get_intraday",
        "mock_alpha_vantage_get_company_overview_amazon",
        "mock_alpha_vantage_get_daily_adjusted_amazon",
    )
    def test_publishes_reminder_when_remind_on_is_today_and_stock_did_not_change(
        self, reminder, mock_tweepy, mock_giphy
    ):
        reminder.stock_price = 3112.70
        reminder.save()
        with freeze_time(reminder.remind_on):
            bot.publish_reminders()

        expected_calls = [
            call().media_upload("random.gif"),
            call().update_status(
                status="@user_name 3 months ago you bought $AMZN at $3,112.70. "
                "It is now worth $3,112.70. That's a return of 0.0%! 🤷‍♂️",
                media_ids=[ANY],
                in_reply_to_status_id=1,
            ),
        ]
        mock_giphy.assert_called_once_with(const.ZERO_RETURN_TAGS)
        assert expected_calls in mock_tweepy.mock_calls
        assert reminder.refresh_from_db().is_finished is True

    @pytest.mark.usefixtures(
        "mock_alpha_vantage_get_intraday_tesla",
        "mock_alpha_vantage_get_company_overview_tesla",
        "mock_alpha_vantage_get_daily_adjusted_tesla",
    )
    def test_publishes_reminder_when_remind_on_is_today_and_stock_was_split(
        self, reminder, mock_tweepy, mock_giphy
    ):
        reminder.created_on = date(2020, 8, 1)
        reminder.remind_on = datetime(2020, 12, 21, 16, 0)
        reminder.stock_symbol = "TSLA"
        reminder.stock_price = 2186.27
        reminder.save()

        with freeze_time(reminder.remind_on):
            bot.publish_reminders()

        expected_calls = [
            call().media_upload("random.gif"),
            call().update_status(
                status="@user_name 4 months ago you bought $TSLA at $2,186.27 "
                "($437.25 after adjusting for the stock split). It is "
                "now worth $661.70. That's a return of 51.33%! 🚀🤑📈",
                media_ids=[ANY],
                in_reply_to_status_id=1,
            ),
        ]

        mock_giphy.assert_called_once_with(const.POSITIVE_RETURN_TAGS)
        assert expected_calls in mock_tweepy.mock_calls
        assert reminder.refresh_from_db().is_finished is True

    @pytest.mark.usefixtures(
        "mock_alpha_vantage_get_intraday_jnj",
        "mock_alpha_vantage_get_company_overview_jnj",
        "mock_alpha_vantage_get_daily_adjusted_jnj",
    )
    def test_publishes_reminder_when_remind_on_is_today_and_dividend_was_paid(
        self, reminder, mock_tweepy, mock_giphy
    ):

        reminder.created_on = date(2020, 6, 1)
        reminder.remind_on = datetime(2020, 12, 30, 16, 0)
        reminder.stock_symbol = "JNJ"
        reminder.stock_price = 149.60
        reminder.save()

        with freeze_time(reminder.remind_on):
            bot.publish_reminders()

        expected_calls = [
            call().media_upload("random.gif"),
            call().update_status(
                status="@user_name 6 months ago you bought $JNJ at $149.60. "
                "It is now worth $157.11 and a total dividend of "
                "$1.01 was paid out. That's a return of 5.7%! 🚀🤑📈",
                media_ids=[ANY],
                in_reply_to_status_id=1,
            ),
        ]

        mock_giphy.assert_called_once_with(const.POSITIVE_RETURN_TAGS)
        assert expected_calls in mock_tweepy.mock_calls
        assert reminder.refresh_from_db().is_finished is True

    @pytest.mark.usefixtures(
        "mock_alpha_vantage_get_intraday",
        "mock_alpha_vantage_get_company_overview_amazon",
        "mock_alpha_vantage_get_daily_adjusted_amazon",
    )
    def test_publishes_reminder_when_stock_was_shorted(self, reminder, mock_tweepy):
        reminder.short = True
        reminder.save()
        with freeze_time(reminder.remind_on):
            bot.publish_reminders()

        expected_calls = [
            call().media_upload("random.gif"),
            call().update_status(
                status="@user_name 3 months ago you shorted $AMZN at $2,954.91. "
                "It is now worth $3,112.70. That's a return of -5.34%! 😭📉",
                media_ids=[ANY],
                in_reply_to_status_id=1,
            ),
        ]

        assert expected_calls in mock_tweepy.mock_calls
        assert reminder.refresh_from_db().is_finished is True

    def test_does_not_publish_reminder_when_reminder_date_is_not_today(
        self, reminder, mock_tweepy
    ):
        with freeze_time("2020-12-14T15:32:00Z"):
            bot.publish_reminders()

        mock_tweepy.assert_not_called()
        assert reminder.refresh_from_db().is_finished is False
