import tweepy
from os import environ


def init_tweepy():
    auth = tweepy.OAuthHandler(environ["CONSUMER_KEY"], environ["CONSUMER_SECRET"])
    auth.set_access_token(environ["ACCESS_TOKEN"], environ["ACCESS_TOKEN_SECRET"])
    return tweepy.API(auth)


def reply_to_mentions():
    last_replied_mention_id = None
    api = init_tweepy()
    new_mentions = api.mentions_timeline(since_id=last_replied_mention_id)
    for mention in new_mentions:
        user = mention.user.screen_name
        api.update_status(
            status=f"@{user} Hey buddy!", in_reply_to_status_id=mention.id
        )
