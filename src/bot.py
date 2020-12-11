import tweepy
from os import environ

from .models import Mention


def init_tweepy():
    auth = tweepy.OAuthHandler(environ["CONSUMER_KEY"], environ["CONSUMER_SECRET"])
    auth.set_access_token(environ["ACCESS_TOKEN"], environ["ACCESS_TOKEN_SECRET"])
    return tweepy.API(auth)


def reply_to_mentions():
    last_replied_mention_id = None
    if Mention.select().exists():
        last_replied_mention_id = (
            Mention.select().order_by(Mention.id.desc()).get().tweet_id
        )
    api = init_tweepy()
    new_mentions = api.mentions_timeline(since_id=last_replied_mention_id)
    for mention in new_mentions:
        Mention(tweet_id=mention.id).save()
        user = mention.user.screen_name
        api = init_tweepy()
        api.update_status(
            status=f"@{user} Hey buddy!", in_reply_to_status_id=mention.id
        )
