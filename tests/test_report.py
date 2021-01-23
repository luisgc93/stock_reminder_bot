import pytest
from unittest.mock import call, ANY

from src import bot
from freezegun import freeze_time


class TestReport:
    @pytest.mark.parametrize(
        "tweet",
        ["report for $JNJ", "analyse $AMZN info", "analyze $ETH"],
    )
    def test_returns_true_when_tweet_contains_report(self, tweet):
        assert bot.demands_report(tweet) is True

    @pytest.mark.parametrize(
        "tweet",
        ["info about $JNJ", "should I buy $AMZN?"],
    )
    def test_returns_false_when_tweet_does_not_contain_report(self, tweet):
        assert bot.demands_report(tweet) is False

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
