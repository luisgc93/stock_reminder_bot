import pytz
import tweepy
from os import environ

from . import const
from .models import Mention, Reminder
from dateutil.parser import parse
from datetime import datetime

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
            Reminder(
                tweet_id=mention.id,
                published_at=datetime.today(),
                reminder_date=parse_reminder_date(tweet),
                stock_symbol=parse_stock_name(tweet),
                stock_price=0.0,
            ).save()
        user = mention.user.screen_name
        api = init_tweepy()
        api.update_status(
            status=f"@{user} Hey buddy!", in_reply_to_status_id=mention.id
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


def parse_stock_name(string):
    name = string.split("$")[1].split(" ")[0]
    return "".join([x for x in name if x.isalpha()])


def parse_reminder_date(string):
    string = string.split("in ")[1]
    cal = parsedatetime.Calendar()
    time_struct, parse_status = cal.parse(string)
    return datetime(*time_struct[:6], tzinfo=pytz.utc)
