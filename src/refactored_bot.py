import os
import random
import re
from datetime import date, datetime

import pytz
from parsedatetime import parsedatetime
from tweepy import TweepError

import const
from dateutil.parser import parse
import pandas as pd
import dataframe_image as dfi

from models import Reminder


class Bot:
    def __init__(self, twitter_client, financial_api_client, gif_client):
        self.twitter_client = twitter_client
        self.stocks_client = financial_api_client
        self.gif_client = gif_client

    def get_mentions(self):
        self.twitter_client.get_mentions()

    def reply_to_mentions(self, mentions):
        for mention in mentions:
            tweet = mention.text
            try:
                if not self._is_valid(tweet) and not mention.in_reply_to_status_id:
                    self._reply_with_help_message(mention)
                    return
                stocks = self._parse_stock_symbols(tweet)
                if self._demands_report(tweet):
                    stock = stocks[0].replace("$", "")
                    self._reply_with_report(mention, stock)
                    return
                if mention.in_reply_to_status_id:
                    self._reply_to_threaded_mention(mention)
                    return
                remind_on = self._calculate_reminder_date(tweet)
                for stock in stocks:
                    self._create_reminder(mention, stock.replace("$", ""))
                self._reply_with_reminder_created_message(mention, remind_on)
            except (KeyError, IndexError):
                self._reply_with_stock_not_found_message(mention)

    def _reply_with_help_message(self, mention):
        user = mention.user.screen_name
        message = f"@{user} {const.HELP_MESSAGE}"
        self.twitter_client.publish(message, mention.id)

    def _reply_with_stock_not_found_message(self, mention):
        message = f"@{mention.user.screen_name} {const.STOCK_NOT_FOUND_RESPONSE}"
        self.twitter_client.publish(message, mention.id)

    def _reply_with_reminder_created_message(self, mention, remind_on):
        stocks = self._parse_stock_symbols(mention.text)
        if len(stocks) > 1:
            stocks[-1] = "and " + stocks[-1]
            stocks[:-2] = [stock + "," for stock in stocks[:-2]]

        message = f"@{mention.user.screen_name} " \
                  f"{random.choice(const.CONFIRMATION_MESSAGES)} I'll remind you "\
                  f"of the price of {' '.join(stocks)} on "\
                  f"{remind_on.strftime('%A %B %d %Y')}. "\
                  f"I hope you make tons of money! 🤑"

        self.twitter_client.publish(message, mention.id)

    def _reply_to_threaded_mention(self, mention):
        try:
            original_tweet = self.twitter_client.get_status(mention.in_reply_to_status_id).text
            if not self._contains_stock(original_tweet) or not self._contains_date(mention.text):
                self._reply_with_help_message(mention)
                return
            stocks = self._parse_stock_symbols(original_tweet)
            remind_on = self._calculate_reminder_date(mention.text)
            for stock in stocks:
                self._create_reminder(mention, stock.replace("$", ""))
            mention.text += " ".join(stocks)
            self._reply_with_reminder_created_message(mention, remind_on)
        except TweepError:
            self._reply_with_help_message(mention)
            return

    def _reply_with_report(self, mention, stock):
        self._generate_report(stock)
        user = mention.user.screen_name
        response = (
            const.CRYPTO_REPORT_RESPONSE + stock + ":"
            if stock in const.CRYPTO_CURRENCIES
            else (const.REPORT_RESPONSE + stock + self.stocks_client.generate_rating(stock))
        )

        media = self.twitter_client.media_upload(const.REPORT_FILE_NAME)
        self.twitter_client.publish(f"@{user} {response}", mention.id, [media.media_id])
        self._remove_file(const.REPORT_FILE_NAME)

    def _generate_report(self, stock):
        if stock.replace("$", "") in const.CRYPTO_CURRENCIES:
            data, _ = self.stocks_client.currencies.get_digital_crypto_rating(stock)
        else:
            data, _ = self.stocks_client.stocks.get_company_overview(stock)
            for (key, val) in list(data.items()):
                if val.isnumeric():
                    data[key] = "${:,.2f}".format(float(val))
                if key not in const.REPORT_FIELDS:
                    data.pop(key)
        self._save_report_to_image(data)

    def _save_report_to_image(self, data):
        df = pd.DataFrame(data, index=[""]).T
        dfi.export(df, const.REPORT_FILE_NAME, table_conversion=None, fontsize=12)

    def _create_reminder(self, mention, stock) -> Reminder:
        price = self.stocks_client.get_price(stock)
        values = {
            "user_name": mention.user.screen_name,
            "tweet_id": mention.id,
            "created_on": date.today(),
            "remind_on": self._calculate_reminder_date(mention.text),
            "stock_symbol": stock,
            "stock_price": price,
            "short": "short" in mention.text.lower(),
        }
        return Reminder.create_instance(values)

    def _calculate_reminder_date(self, tweet):
        cal = parsedatetime.Calendar(version=parsedatetime.VERSION_CONTEXT_STYLE)
        result, _ = cal.parseDT(tweet, tzinfo=pytz.utc, sourceTime=datetime.now())
        return result

    def _is_valid(self, tweet):
        return self._demands_report(tweet) or self._contains_stock(tweet) and self._contains_date(tweet)

    def _contains_stock(self, tweet):
        return const.CASHTAG in tweet

    def _contains_date(self, tweet):
        if any([string in tweet for string in const.DATE_TIME_STRINGS]):
            return True
        try:
            parse(tweet, fuzzy=True)
            return True
        except ValueError:
            return False

    def _parse_stock_symbols(self, tweet):
        return re.findall(r"[$][A-Za-z]*", tweet)

    def _demands_report(self, tweet):
        return any(
            keyword in tweet.lower() for keyword in const.REPORT_KEYWORDS
        ) and self._contains_stock(tweet)

    def _calculate_returns(self, original_price, current_price, dividend):
        return round(
            ((current_price - original_price + dividend) / original_price) * 100, 2
        )

    def _remove_file(self, file):
        os.remove(file) if os.path.exists(file) else None

