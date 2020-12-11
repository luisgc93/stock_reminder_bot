import tweepy
from os import environ


def init_tweepy():
    auth = tweepy.OAuthHandler(environ["CONSUMER_KEY"], environ["CONSUMER_SECRET"])
    auth.set_access_token(environ["ACCESS_TOKEN"], environ["ACCESS_TOKEN_SECRET"])
    return tweepy.API(auth)


def reply_to_mentions():
    api = init_tweepy()
    api.update_status(
        status="Hello world!"
    )
