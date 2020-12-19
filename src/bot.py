import tweepy
from os import environ

from alpha_vantage.timeseries import TimeSeries

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
        if contains_stock(tweet) and contains_date(tweet):
            reminder = create_reminder(mention, tweet)
            api = init_tweepy()
            user = mention.user.screen_name
            api.update_status(
                status=f"@{user} Sure thing buddy! I'll remind you "
                f"of the price of ${reminder.stock_symbol} on "
                f"{reminder.remind_on.strftime('%A %B %d %Y')}. "
                f"I hope you make tons of money! 🤑",
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
            f"${reminder.stock_symbol} at ${reminder.stock_price:.2f}. "
            f"It is now worth ${current_price:.2f}. That's a return of"
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


def create_reminder(mention, tweet):
    stock = parse_stock_symbol(tweet)
    price = get_price(stock)
    return Reminder.create(
        user_name=mention.user.screen_name,
        tweet_id=mention.id,
        created_on=date.today(),
        remind_on=calculate_reminder_date(tweet),
        stock_symbol=stock,
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


def parse_stock_symbol(string):
    name = string.split("$")[1].split(" ")[0]
    return "".join([x for x in name if x.isalpha()])


def calculate_reminder_date(string):
    cal = parsedatetime.Calendar()
    time_struct, parse_status = cal.parse(string)
    return date(*time_struct[:3])


def calculate_time_delta(today, created_on):
    return humanize.naturaldelta(today - created_on)


def get_price(stock):
    ts = TimeSeries(key=environ["ALPHA_VANTAGE_API_KEY"])
    data, _ = ts.get_quote_endpoint(stock)
    full_price = data["05. price"]

    return float(full_price[:-2])


def calculate_returns(original_price, current_price):
    return round(((current_price - original_price) / original_price) * 100, 2)
