import pytest
from unittest.mock import call

from src import bot
from src.models import Mention


class TestBot:
    @pytest.mark.usefixtures("mock_new_mention")
    def test_saves_new_mentions(self, mock_tweepy):
        assert Mention.select().count() == 0

        bot.reply_to_mentions()

        mock_tweepy.assert_has_calls([call().mentions_timeline(since_id=None)])
        assert Mention.select().count() == 1
