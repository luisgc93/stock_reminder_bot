import random
import urllib.request
from os import environ

from giphy_client import DefaultApi

import const


class GifClient:
    def __init__(self, api: DefaultApi):
        self.api = api

    def download_random_gif(self, tags):
        open(const.GIF_FILE_NAME, "w")
        gif_url = (
            self.api.gifs_search_get(
                environ["GIPHY_API_KEY"], random.choice(tags), limit=3, offset=3, fmt="json"
            ).data[random.choice(range(3))].images.original.url
        )
        urllib.request.urlretrieve(gif_url, const.GIF_FILE_NAME)

    def download_pre_selected_gif(self, url):
        urllib.request.urlretrieve(url, const.GIF_FILE_NAME)
