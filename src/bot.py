import re

import tweepy
from os import environ

from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.foreignexchange import ForeignExchange
from alpha_vantage.fundamentaldata import FundamentalData

from . import const
from .models import Reminder
from dateutil.parser import parse
from datetime import date, datetime, timedelta
import humanize

import parsedatetime


def init_tweepy():
    auth = tweepy.OAuthHandler(environ["CONSUMER_KEY"], environ["CONSUMER_SECRET"])
    auth.set_access_token(environ["ACCESS_TOKEN"], environ["ACCESS_TOKEN_SECRET"])
    return tweepy.API(auth)


def update_reminders():
    for reminder in Reminder.select():
        reminder.remind_on_new = datetime.combine(
            reminder.remind_on, datetime.min.time()
        ) + timedelta(hours=12)
        reminder.save()


def reply_to_mentions():
    api = init_tweepy()
    new_mentions = api.mentions_timeline(since_id=get_last_replied_tweet_id(api))
    for mention in new_mentions:
        tweet = mention.text
        user = mention.user.screen_name
        if not is_valid(tweet):
            api.update_status(
                status=f"@{user} {const.INVALID_MENTION_RESPONSE}",
                in_reply_to_status_id=mention.id,
            )
            return
        try:
            stocks = parse_stock_symbols(tweet)
            remind_on = calculate_reminder_date(tweet)
            for stock in stocks:
                create_reminder(mention, tweet, stock.replace("$", ""))
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
        except (ValueError, IndexError) as e:
            exc_mapper = {
                ValueError: const.API_LIMIT_EXCEEDED_RESPONSE,
                IndexError: const.STOCK_NOT_FOUND_RESPONSE,
            }
            api.update_status(
                status=f"@{user} {exc_mapper[e.__class__]}",
                in_reply_to_status_id=mention.id,
            )


def publish_reminders():
    update_reminders()
    for reminder in Reminder.due_today():
        api = init_tweepy()
        split_factor = get_split_factor(reminder)
        original_adjusted_price = reminder.stock_price / split_factor
        current_price = get_price(reminder.stock_symbol)
        rate_of_return = calculate_returns(original_adjusted_price, current_price)
        stock_split_message = "."
        if split_factor != 1.0:
            stock_split_message = (
                f" (${'{:,.2f}'.format(original_adjusted_price)} "
                f"after adjusting for the stock split)."
            )

        time_since_created_on = calculate_time_delta(date.today(), reminder.created_on)
        status = (
            f"@{reminder.user_name} {time_since_created_on} ago you bought "
            f"${reminder.stock_symbol} at ${'{:,.2f}'.format(reminder.stock_price)}"
            f"{stock_split_message} It is now worth ${'{:,.2f}'.format(current_price)}."
            f" That's a return of {rate_of_return}%! "
        )
        if rate_of_return >= 0:
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

        reminder.finish()


def create_reminder(mention, tweet, stock):
    price = get_price(stock)
    return Reminder.create(
        user_name=mention.user.screen_name,
        tweet_id=mention.id,
        created_on=date.today(),
        remind_on=calculate_reminder_date(tweet),
        stock_symbol=stock,
        stock_price=price,
    )


def get_last_replied_tweet_id(client):
    return client.user_timeline(id=environ["BOT_USER_ID"], count=1)[0].id


def is_valid(tweet):
    return contains_stock(tweet) and contains_date(tweet)


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
    return re.findall(r"[$][A-Za-z]*", tweet)


def remove_lower_case_chars(string):
    return "".join(char for char in string if char.isupper())


def calculate_reminder_date(tweet):
    cal = parsedatetime.Calendar(version=parsedatetime.VERSION_CONTEXT_STYLE)
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
        data, meta_data = ts.get_intraday(stock)
        key = list(data.keys())[0]
        full_price = data[key]["1. open"]
    return float(full_price[:-2])


def get_split_factor(reminder):
    if reminder.stock_symbol in const.CRYPTO_CURRENCIES:
        return 1.0

    fd = FundamentalData(key=environ["ALPHA_VANTAGE_API_KEY"])
    data, _ = fd.get_company_overview(reminder.stock_symbol)

    if data["LastSplitDate"] == "None":
        return 1.0
    split_date = datetime.strptime(data["LastSplitDate"], "%Y-%m-%d").date()
    stock_was_split = reminder.created_on < split_date < date.today()
    if stock_was_split:
        return float(data["LastSplitFactor"][0]) / float(data["LastSplitFactor"][2])
    return 1.0


def calculate_returns(original_price, current_price):
    return round(((current_price - original_price) / original_price) * 100, 2)
