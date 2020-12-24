import re

import tweepy
from os import environ

from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.foreignexchange import ForeignExchange

from . import const
from .models import Mention, Reminder
from dateutil.parser import parse
from datetime import date
import humanize

import parsedatetime


def init_tweepy():
    auth = tweepy.OAuthHandler(environ["CONSUMER_KEY"], environ["CONSUMER_SECRET"])
    auth.set_access_token(environ["ACCESS_TOKEN"], environ["ACCESS_TOKEN_SECRET"])
    return tweepy.API(auth)


def reply_to_mentions():
    api = init_tweepy()
    new_mentions = api.mentions_timeline(since_id=get_last_replied_mention_id())
    for mention in new_mentions:
        Mention(tweet_id=mention.id).save()
        tweet = mention.text
        user = mention.user.screen_name
        if contains_stock(tweet) and contains_date(tweet):
            try:
                stocks = parse_stock_symbols(tweet)
                remind_on = calculate_reminder_date(tweet)
                for stock in stocks:
                    create_reminder(mention, tweet, stock)
                api = init_tweepy()
                if len(stocks) > 1:
                    stocks[-1] = "and " + stocks[-1]
                    stocks[:-2] = [stock + "," for stock in stocks[:-2]]
                api.update_status(
                    status=f"@{user} Sure thing buddy! I'll remind you "
                    f"of the price of {' '.join(stocks)} on "
                    f"{remind_on.strftime('%A %B %d %Y')}. "
                    f"I hope you make tons of money! 🤑",
                    in_reply_to_status_id=mention.id,
                )
            except (ValueError, KeyError) as e:
                exc_mapper = {
                    ValueError: const.API_LIMIT_EXCEEDED_RESPONSE,
                    KeyError: const.STOCK_NOT_FOUND_RESPONSE,
                }
                api.update_status(
                    status=f"@{user} {exc_mapper[e.__class__]}",
                    in_reply_to_status_id=mention.id,
                )


def reply_to_reminders():
    today = date.today()
    reminders = Reminder.select().where(Reminder.remind_on == today)
    for reminder in reminders:
        api = init_tweepy()
        time_since_created_on = calculate_time_delta(today, reminder.created_on)
        original_price = reminder.stock_price
        current_price = get_price(reminder.stock_symbol)
        total_returns = calculate_returns(original_price, current_price)
        status = (
            f"@{reminder.user_name} {time_since_created_on} ago you bought "
            f"${reminder.stock_symbol} at ${'{:,.2f}'.format(reminder.stock_price)}. "
            f"It is now worth ${'{:,.2f}'.format(current_price)}. That's a return of"
            f" {total_returns}%! "
        )
        if current_price >= original_price:
            api.update_with_media(
                filename=const.MR_SCROOGE_IMAGE_PATH,
                status=status + const.POSITIVE_RETURNS_EMOJI,
                in_reply_to_status_id=reminder.tweet_id,
            )
        else:
            api.update_with_media(
                filename=const.MR_BURNS_IMAGE_PATH,
                status=status + const.NEGATIVE_RETURNS_EMOJI,
                in_reply_to_status_id=reminder.tweet_id,
            )


def create_reminder(mention, tweet, stock):
    price = get_price(stock)
    return Reminder.create(
        user_name=mention.user.screen_name,
        tweet_id=mention.id,
        created_on=date.today(),
        remind_on=calculate_reminder_date(tweet),
        stock_symbol=stock.replace("$", ""),
        stock_price=price,
    )


def get_last_replied_mention_id():
    if not Mention.select().exists():
        return
    last_replied_mention_id = (
        Mention.select().order_by(Mention.id.desc()).get().tweet_id
    )
    return last_replied_mention_id


def contains_stock(tweet):
    return const.CASHTAG in tweet


def contains_date(tweet):
    if any([string in tweet for string in const.DATE_TIME_STRINGS]):
        return True
    try:
        parse(tweet, fuzzy=True)
        return True
    except ValueError:
        return False


def parse_stock_symbols(tweet):
    return re.findall(r"[$][A-Z]*", tweet)


def remove_lower_case_chars(string):
    return "".join(char for char in string if char.isupper())


def calculate_reminder_date(tweet):
    cal = parsedatetime.Calendar()
    time_struct, parse_status = cal.parse(tweet)
    return date(*time_struct[:3])


def calculate_time_delta(today, created_on):
    return humanize.naturaldelta(today - created_on)


def get_price(stock):
    if stock in const.CRYPTO_CURRENCIES:
        fe = ForeignExchange(key=environ["ALPHA_VANTAGE_API_KEY"])
        data, _ = fe.get_currency_exchange_rate(stock, "USD")
        full_price = data["5. Exchange Rate"]

    else:
        ts = TimeSeries(key=environ["ALPHA_VANTAGE_API_KEY"])
        data, _ = ts.get_quote_endpoint(stock)
        full_price = data["05. price"]
    return float(full_price[:-2])


def calculate_returns(original_price, current_price):
    return round(((current_price - original_price) / original_price) * 100, 2)
