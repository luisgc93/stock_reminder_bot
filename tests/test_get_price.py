import pytest

from src import bot
from freezegun import freeze_time


class TestGetPrice:
    def test_returns_price_for_stock(self, mock_alpha_vantage_get_intraday_amazon):
        with freeze_time("2021-01-07T15:31:00Z"):
            price = bot.get_price("AMZN")

        assert price == 3112.70
        mock_alpha_vantage_get_intraday_amazon.assert_called_once_with("AMZN")

    @pytest.mark.usefixtures("mock_alpha_vantage_max_retries_exceeded")
    def test_uses_fmp_api_as_fallback_when_alpha_vantage_api_limit_exceeded(
        self, mock_fmp_api_get_price_response
    ):
        with freeze_time("2021-01-07T15:31:00Z"):
            price = bot.get_price("AAPL")

        assert price == 126.66
        mock_fmp_api_get_price_response.assert_called_once()

    def test_returns_price_for_cryptocurrency(
        self, mock_alpha_vantage_get_currency_exchange_rate
    ):
        price = bot.get_price("bitcoin")

        assert price == 23933.49
        mock_alpha_vantage_get_currency_exchange_rate.assert_called_once_with(
            "BTC", "USD"
        )

    @pytest.mark.parametrize(
        "current_time",
        ["2021-01-07T14:31:00Z", "2021-01-07T15:52:00Z", "2021-01-07T20:59:00Z"],
    )
    def test_returns_true_when_market_is_open(self, current_time):
        with freeze_time(current_time):
            assert bot.nasdaq_is_open()

    @pytest.mark.parametrize(
        "current_time",
        ["2021-01-07T09:30:00Z", "2021-01-07T14:29:00Z", "2021-01-09T14:31:00Z"],
    )
    def test_returns_false_when_market_is_closed(self, current_time):
        with freeze_time(current_time):
            assert bot.nasdaq_is_open() is False

    def test_uses_get_quote_endpoint_when_market_is_closed(
        self, mock_alpha_vantage_get_quote_amazon
    ):
        with freeze_time("2021-01-07T09:30:00Z"):
            price = bot.get_price("AMZN")

        assert price == 3138.38
        mock_alpha_vantage_get_quote_amazon.assert_called_once_with("AMZN")
