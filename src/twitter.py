from os import environ

import tweepy


class TwitterClient:
    def __init__(self, credentials):
        auth = tweepy.OAuthHandler(credentials['api_key'], credentials['api_key_secret'])
        auth.set_access_token(credentials['access_token'], credentials['access_token_secret'])
        self.api = tweepy.API(auth)

    def get_mentions(self):
        tweet_id = self._get_last_replied_tweet_id()
        return self.api.mentions_timeline(since_id=tweet_id)

    def _get_last_replied_tweet_id(self):
        return self.api.user_timeline(id=environ["BOT_USER_ID"], count=1)[0].id

    def publish(self, message, in_reply_to_status_id=None, media_ids=[]):
        self.api.update_status(
            status=message,
            in_reply_to_status_id=in_reply_to_status_id,
            media_ids=media_ids
        )
