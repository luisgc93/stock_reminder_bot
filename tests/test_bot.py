from datetime import date, datetime

import pytest
from unittest.mock import call, ANY

import pytz

from src import bot, const
from src.models import Reminder
from freezegun import freeze_time


class TestReplyToMentions:
    @pytest.mark.usefixtures("mock_mention")
    def test_creates_reminder_when_mention_contains_stock_and_date(
        self, mock_alpha_vantage_get_intraday_amazon
    ):
        assert Reminder.select().count() == 0

        with freeze_time("2020-12-11T15:32:00Z"):
            bot.reply_to_mentions()

        assert Reminder.select().count() == 1

        reminder = Reminder.select().first()
        assert reminder.tweet_id == 1
        assert reminder.created_on == date(2020, 12, 11)
        assert reminder.remind_on == "2021-03-11 15:32:00+00:00"
        assert reminder.stock_symbol == "AMZN"
        assert reminder.stock_price == 3112.70
        assert reminder.is_finished is False
        mock_alpha_vantage_get_intraday_amazon.assert_called_once_with("AMZN")

    @pytest.mark.usefixtures(
        "mock_mention_with_multiple_stocks", "mock_alpha_vantage_get_intraday_amazon"
    )
    def test_creates_reminders_when_mention_contains_multiple_stocks_and_date(
        self,
    ):
        assert Reminder.select().count() == 0

        with freeze_time("2020-12-11T15:32:00Z"):
            bot.reply_to_mentions()

        reminders = Reminder.select()
        assert reminders.count() == 4
        assert [reminder.stock_symbol for reminder in reminders] == [
            "AMZN",
            "MSFT",
            "AAPL",
            "BABA",
        ]

    @pytest.mark.usefixtures("mock_mention", "mock_alpha_vantage_get_intraday_amazon")
    def test_replies_to_mention_when_reminder_created(self, mock_tweepy, mock_giphy):
        with freeze_time("2020-12-11T15:32:00Z"):
            bot.reply_to_mentions()

        expected_calls = [
            call().media_upload("random.gif"),
            call().update_status(
                status="@user_name Sure thing buddy! I'll remind you of the price of "
                "$AMZN on Thursday March 11 2021. I hope you make tons of money! 🤑",
                in_reply_to_status_id=1,
                media_ids=[ANY],
            ),
        ]

        mock_giphy.assert_called_once_with(const.FINGERS_CROSSED_GIF_TAG)
        assert Reminder.select().count() == 1
        assert expected_calls in mock_tweepy.mock_calls

    @pytest.mark.usefixtures(
        "mock_mention_with_multiple_stocks", "mock_alpha_vantage_get_intraday_amazon"
    )
    def test_replies_when_multiple_reminders_created(self, mock_tweepy, mock_giphy):
        with freeze_time("2020-12-11T15:32:00Z"):
            bot.reply_to_mentions()

        expected_calls = [
            call().media_upload("random.gif"),
            call().update_status(
                status="@user_name Sure thing buddy! I'll remind you of the price of "
                "$AMZN, $MSFT, $AAPL and $BABA on Thursday March 11 2021. I hope you "
                "make tons of money! 🤑",
                in_reply_to_status_id=1,
                media_ids=[ANY],
            ),
        ]

        mock_giphy.assert_called_once_with(const.FINGERS_CROSSED_GIF_TAG)
        assert Reminder.select().count() == 4
        assert expected_calls in mock_tweepy.mock_calls

    @pytest.mark.usefixtures("mock_mention_with_invalid_format")
    def test_replies_when_mention_is_not_valid(self, mock_tweepy):
        with freeze_time("2020-12-13T15:32:00Z"):
            bot.reply_to_mentions()

        expected_status_call = call().update_status(
            status=f"@user_name {const.INVALID_MENTION_RESPONSE}",
            in_reply_to_status_id=1,
        )

        assert expected_status_call in mock_tweepy.mock_calls
        assert Reminder.select().count() == 0

    @pytest.mark.usefixtures("mock_mention", "mock_alpha_vantage_stock_not_found")
    def test_replies_when_stock_is_not_found(self, mock_tweepy):
        with freeze_time("2020-12-11T15:32:00Z"):
            bot.reply_to_mentions()

        expected_status_call = call().update_status(
            status=f"@user_name {const.STOCK_NOT_FOUND_RESPONSE}",
            in_reply_to_status_id=1,
        )

        assert expected_status_call in mock_tweepy.mock_calls

    @pytest.mark.usefixtures(
        "mock_alpha_vantage_get_company_overview_amazon",
        "mock_mention_asking_for_report",
        "mock_fmp_api_rating_response",
    )
    def test_replies_with_company_report_when_mention_contains_report_and_stock(
        self,
        mock_tweepy,
    ):
        with freeze_time("2020-12-13T15:32:00Z"):
            bot.reply_to_mentions()

        expected_status_call = call().update_status(
            status="@user_name Knowledge is power! 🧠💪 Here is your company "
            "report for $AMZN. Score: 4, Rating: A+, Recommendation: Buy. Details: ",
            in_reply_to_status_id=1,
            media_ids=[ANY],
        )

        assert expected_status_call in mock_tweepy.mock_calls

    @pytest.mark.usefixtures(
        "mock_alpha_vantage_crypto_rating", "mock_mention_asking_for_crypto_report"
    )
    def test_replies_with_company_report_when_mention_contains_report_and_crypto(
        self,
        mock_tweepy,
    ):
        with freeze_time("2020-12-13T15:32:00Z"):
            bot.reply_to_mentions()

        expected_status_call = call().update_status(
            status="@user_name Knowledge is power! 🧠💪 Here "
            "is your crypto ratings report for $ETH:",
            in_reply_to_status_id=1,
            media_ids=[ANY],
        )

        assert expected_status_call in mock_tweepy.mock_calls


class TestPublishReminders:
    @pytest.mark.usefixtures(
        "mock_alpha_vantage_get_intraday_amazon",
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
        assert Reminder().get_by_id(reminder.id).is_finished is True

    @pytest.mark.usefixtures(
        "mock_alpha_vantage_get_intraday_amazon",
        "mock_alpha_vantage_get_company_overview_amazon",
        "mock_alpha_vantage_get_daily_adjusted_amazon",
    )
    def test_publishes_reminder_when_remind_on_is_today_and_stock_went_down(
        self, reminder, mock_tweepy, mock_giphy
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

        assert expected_calls in mock_tweepy.mock_calls
        assert Reminder().get_by_id(reminder.id).is_finished is True

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
        assert Reminder().get_by_id(reminder.id).is_finished is True

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
        assert Reminder().get_by_id(reminder.id).is_finished is True

    def test_does_not_publish_reminder_when_reminder_date_is_not_today(
        self, reminder, mock_tweepy
    ):
        with freeze_time("2020-12-14T15:32:00Z"):
            bot.publish_reminders()

        mock_tweepy.assert_not_called()
        assert Reminder().get_by_id(reminder.id).is_finished is False


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
        "tweet",
        ["report for $JNJ", "analyse $AMZN info"],
    )
    def test_returns_true_when_tweet_contains_report(self, tweet):
        assert bot.demands_report(tweet) is True

    @pytest.mark.parametrize(
        "tweet, stock_tickers",
        [
            ("$AMZN in 7 months", ["$AMZN"]),
            ("$msft 1/28/2021", ["$msft"]),
            (
                "Remind me next year of: $VEEV $ABBV $DOCU $ADYEN $GOOG $IRM $DLR",
                ["$VEEV", "$ABBV", "$DOCU", "$ADYEN", "$GOOG", "$IRM", "$DLR"],
            ),
            (
                "Remind me of $AMZN, $AAPL and $BABA in 3 months.",
                ["$AMZN", "$AAPL", "$BABA"],
            ),
            ("$DDOG and $SNOW in 6 months", ["$DDOG", "$SNOW"]),
        ],
    )
    def test_returns_stock_tickers_when_tweet_contains_stocks(
        self, tweet, stock_tickers
    ):

        assert bot.parse_stock_symbols(tweet) == stock_tickers

    @pytest.mark.parametrize(
        "string, reminder_date",
        [
            ("tomorrow", datetime(2020, 12, 14, 9, 0, tzinfo=pytz.utc)),
            ("In 3 days", datetime(2020, 12, 16, 15, 32, tzinfo=pytz.utc)),
            ("in one week", datetime(2020, 12, 20, 15, 32, tzinfo=pytz.utc)),
            ("in two months", datetime(2021, 2, 13, 15, 32, tzinfo=pytz.utc)),
            ("$MSFT in 2 years", datetime(2022, 12, 13, 15, 32, tzinfo=pytz.utc)),
            ("$BTC in 1 hour", datetime(2020, 12, 13, 16, 32, tzinfo=pytz.utc)),
            ("$BTC in 2 hours", datetime(2020, 12, 13, 17, 32, tzinfo=pytz.utc)),
            ("$BTC in 20 minutes", datetime(2020, 12, 13, 15, 52, tzinfo=pytz.utc)),
        ],
    )
    def test_calculates_reminder_date_from_string(self, string, reminder_date):
        with freeze_time("2020-12-13T15:32:00Z"):
            assert bot.calculate_reminder_date(string) == reminder_date

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


class TestGetPrice:
    def test_returns_price_for_stock(self, mock_alpha_vantage_get_intraday_amazon):
        price = bot.get_price("AMZN")

        assert price == 3112.70
        mock_alpha_vantage_get_intraday_amazon.assert_called_once_with("AMZN")

    @pytest.mark.usefixtures("mock_alpha_vantage_max_retries_exceeded")
    def test_uses_fmp_api_as_backup_when_alpha_vantage_api_limit_exceeded(
        self, mock_fmp_api_get_price_response
    ):
        price = bot.get_price("AAPL")

        assert price == 126.66
        mock_fmp_api_get_price_response.assert_called_once()

    def test_returns_price_for_cryptocurrency(
        self, mock_alpha_vantage_get_currency_exchange_rate
    ):
        price = bot.get_price("BTC")

        assert price == 23933.49
        mock_alpha_vantage_get_currency_exchange_rate.assert_called_once_with(
            "BTC", "USD"
        )

    @pytest.mark.parametrize(
        "current_time",
        ["2021-01-07T15:31:00Z", "2021-01-07T16:52:00Z", "2021-01-07T21:59:00Z"],
    )
    def test_returns_true_when_market_is_open(self, current_time):
        with freeze_time(current_time):
            assert bot.nasdaq_is_open()

    @pytest.mark.parametrize(
        "current_time",
        ["2021-01-07T09:30:00Z", "2021-01-07T15:29:00Z", "2021-01-09T15:31:00Z"],
    )
    def test_returns_false_when_market_is_closed(self, current_time):
        with freeze_time(current_time):
            assert bot.nasdaq_is_open() is False
