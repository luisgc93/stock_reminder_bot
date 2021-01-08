import os
import random
import re

import giphy_client
import pytz

import urllib.request

import requests
import tweepy
from os import environ

from alpha_vantage.cryptocurrencies import CryptoCurrencies
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.foreignexchange import ForeignExchange
from alpha_vantage.fundamentaldata import FundamentalData

from . import const
from .models import Reminder
from dateutil.parser import parse
from datetime import date, datetime, time
import humanize

import parsedatetime

from PIL import Image, ImageDraw, ImageFont

import pandas as pd
import dataframe_image as dfi


def init_tweepy():
    auth = tweepy.OAuthHandler(environ["CONSUMER_KEY"], environ["CONSUMER_SECRET"])
    auth.set_access_token(environ["ACCESS_TOKEN"], environ["ACCESS_TOKEN_SECRET"])
    return tweepy.API(auth)


def reply_to_mentions():
    api = init_tweepy()
    new_mentions = api.mentions_timeline(since_id=get_last_replied_tweet_id(api))
    for mention in new_mentions:
        tweet = mention.text
        if not is_valid(mention.text):
            reply_with_help_message(mention)
            return
        stocks = parse_stock_symbols(tweet)
        if demands_report(tweet):
            stock = stocks[0].replace("$", "")
            reply_with_report(mention, stock)
            return
        try:
            remind_on = calculate_reminder_date(tweet)
            for stock in stocks:
                create_reminder(mention, stock.replace("$", ""))
            reply_with_reminder_created_message(mention, remind_on)
        except (ValueError, IndexError) as e:
            reply_with_error_message(e, mention)


def reply_with_reminder_created_message(mention, remind_on):
    stocks = parse_stock_symbols(mention.text)
    api = init_tweepy()
    if len(stocks) > 1:
        stocks[-1] = "and " + stocks[-1]
        stocks[:-2] = [stock + "," for stock in stocks[:-2]]
    download_random_gif(const.FINGERS_CROSSED_GIF_TAG)
    media = api.media_upload(const.GIF_FILE_NAME)
    api.update_status(
        status=f"@{mention.user.screen_name} "
        f"Sure thing buddy! I'll remind you "
        f"of the price of {' '.join(stocks)} on "
        f"{remind_on.strftime('%A %B %d %Y')}. "
        f"I hope you make tons of money! 🤑",
        in_reply_to_status_id=mention.id,
        media_ids=[media.media_id],
    )
    remove_file(const.GIF_FILE_NAME)


def reply_with_help_message(mention):
    user = mention.user.screen_name
    init_tweepy().update_status(
        status=f"@{user} {const.HELP_MESSAGE}",
        in_reply_to_status_id=mention.id,
    )


def reply_with_report(mention, stock):
    generate_report(stock)
    user = mention.user.screen_name
    response = (
        const.CRYPTO_REPORT_RESPONSE + stock + ":"
        if stock in const.CRYPTO_CURRENCIES
        else (const.REPORT_RESPONSE + stock + ". " + generate_rating(stock))
    )
    if environ["SAVE_RATINGS_IMG"] == "active":
        media = init_tweepy().media_upload("rating_table.png")
    else:
        media = init_tweepy().media_upload(const.REPORT_FILE_NAME)
    init_tweepy().update_status(
        status=f"@{user} {response}",
        in_reply_to_status_id=mention.id,
        media_ids=[media.media_id],
    )
    remove_file(const.REPORT_FILE_NAME)


def reply_with_error_message(e, mention):
    exc_mapper = {
        ValueError: const.API_LIMIT_EXCEEDED_RESPONSE,
        IndexError: const.STOCK_NOT_FOUND_RESPONSE,
    }
    init_tweepy().update_status(
        status=f"@{mention.user.screen_name} {exc_mapper[e.__class__]}",
        in_reply_to_status_id=mention.id,
    )


def publish_reminders():
    for reminder in Reminder.due_now():
        api = init_tweepy()
        status = generate_investment_results(reminder)
        if const.POSITIVE_RETURNS_EMOJI in status:
            download_random_gif(const.POSITIVE_RETURN_TAGS)
        else:
            gif_url = random.choice(const.NEGATIVE_RETURN_GIFS)
            download_pre_selected_gif(gif_url)
        media = api.media_upload(const.GIF_FILE_NAME)
        api.update_status(
            status=status,
            media_ids=[media.media_id],
            in_reply_to_status_id=reminder.tweet_id,
        )
        reminder.finish()
        remove_file(const.GIF_FILE_NAME)


def generate_investment_results(reminder):
    split_factor = get_split_factor(reminder)
    dividend = get_dividend(reminder)
    original_adjusted_price = reminder.stock_price / split_factor
    current_price = get_price(reminder.stock_symbol)
    rate_of_return = calculate_returns(original_adjusted_price, current_price, dividend)
    stock_split_message = "."
    dividend_message = ""
    if split_factor != 1.0:
        stock_split_message = (
            f" (${'{:,.2f}'.format(original_adjusted_price)} "
            f"after adjusting for the stock split)."
        )
    if dividend:
        dividend_message = (
            f" and a total dividend of ${'{:.2f}'.format(dividend)} was paid out"
        )
    time_since_created_on = calculate_time_delta(date.today(), reminder.created_on)
    user_action = "bought"
    if reminder.short:
        rate_of_return *= -1
        user_action = "shorted"
    if rate_of_return > 0:
        emoji = const.POSITIVE_RETURNS_EMOJI
    else:
        emoji = const.NEGATIVE_RETURNS_EMOJI
    return (
        f"@{reminder.user_name} {time_since_created_on} ago you {user_action} "
        f"${reminder.stock_symbol} at ${'{:,.2f}'.format(reminder.stock_price)}"
        f"{stock_split_message} It is now worth ${'{:,.2f}'.format(current_price)}"
        f"{dividend_message}. That's a return of {rate_of_return}%! {emoji}"
    )


def create_reminder(mention, stock):
    price = get_price(stock)
    values = {
        "user_name": mention.user.screen_name,
        "tweet_id": mention.id,
        "created_on": date.today(),
        "remind_on": calculate_reminder_date(mention.text),
        "stock_symbol": stock,
        "stock_price": price,
        "short": "short" in mention.text.lower(),
    }
    return Reminder.create_instance(values)


def get_last_replied_tweet_id(client):
    return client.user_timeline(id=environ["BOT_USER_ID"], count=1)[0].id


def is_valid(tweet):
    return demands_report(tweet) or contains_stock(tweet) and contains_date(tweet)


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


def demands_report(tweet):
    return any(
        keyword in tweet.lower() for keyword in const.REPORT_KEYWORDS
    ) and contains_stock(tweet)


def generate_report(stock):
    if stock.replace("$", "") in const.CRYPTO_CURRENCIES:
        crypto = CryptoCurrencies(key=environ["ALPHA_VANTAGE_API_KEY"])
        data, _ = crypto.get_digital_crypto_rating(stock)
    else:
        fd = FundamentalData(key=environ["ALPHA_VANTAGE_API_KEY"])
        data, _ = fd.get_company_overview(stock)
        for (key, val) in list(data.items()):
            if val.isnumeric():
                data[key] = "${:,.2f}".format(float(val))
            if key not in const.REPORT_FIELDS:
                data.pop(key)

        if data["DividendPerShare"] == "None":
            data.pop("PayoutRatio")
            for key in [key for key in data.keys() if "dividend" in key.lower()]:
                data.pop(key)
                data["DividendPerShare"] = "None"
    save_report_to_image(data)


def generate_rating(stock):
    rating_response = requests.get(
        f'{const.FMP_API_RATING_ENDPOINT}{stock}?apikey={environ["FMP_API_KEY"]}'
    )
    rating_data = rating_response.json()
    ratings_list = [
        (key.capitalize() + ": " + str(value))
        for key, value in rating_data["rating"].items()
    ]
    if environ["SAVE_RATINGS_IMG"] == "active":
        data_formatted = pd.DataFrame(rating_data["ratingDetails"]).T
        dfi.export(
            data_formatted,
            "rating_table.png",
            chrome_path=environ["CHROMEDRIVER_PATH"],
        )
    return ", ".join(ratings_list) + ". Details: "


def save_report_to_image(data):
    img = Image.new("RGB", (600, 38 * len(data)), color=const.REPORT_BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(const.REPORT_FONT_PATH, 15)
    text = "\n\n ".join("{!s}: {!s}".format(key, val) for (key, val) in data.items())
    draw.text((14, 14), text, font=font, fill=const.REPORT_FONT_COLOR)
    img.save(const.REPORT_FILE_NAME)


def remove_lower_case_chars(string):
    return "".join(char for char in string if char.isupper())


def calculate_reminder_date(tweet):
    cal = parsedatetime.Calendar(version=parsedatetime.VERSION_CONTEXT_STYLE)
    result, _ = cal.parseDT(tweet, tzinfo=pytz.utc, sourceTime=datetime.now())
    return result


def calculate_time_delta(today, created_on):
    return humanize.naturaldelta(today - created_on)


def get_price(stock):
    if stock in const.CRYPTO_CURRENCIES:
        fe = ForeignExchange(key=environ["ALPHA_VANTAGE_API_KEY"])
        data, _ = fe.get_currency_exchange_rate(stock, "USD")
        full_price = data["5. Exchange Rate"]
        return float(full_price[:-2])
    else:
        try:
            ts = TimeSeries(key=environ["ALPHA_VANTAGE_API_KEY"])
            if nasdaq_is_open():
                data, meta_data = ts.get_intraday(stock)
                key = list(data.keys())[0]
                full_price = data[key]["4. close"]
                return float(full_price[:-2])
            else:
                data = ts.get_quote_endpoint(stock)
                full_price = data["05. price"]
                return float(full_price[:-2])
        except ValueError:
            response = requests.get(
                f"{const.FMP_API_GET_PRICE_ENDPOINT}"
                f'{stock}?apikey={environ["FMP_API_KEY"]}'
            )
            return response.json()[0]["price"]


def nasdaq_is_open():
    nyc_now = datetime.now(pytz.timezone("US/Eastern"))
    if nyc_now.weekday() in const.WEEKEND_DAYS:
        return False
    nyc_time = nyc_now.time()
    open_time = time(hour=9, minute=30)
    closing_time = time(hour=16, minute=00)
    return closing_time >= nyc_time >= open_time


def get_split_factor(reminder):
    if reminder.stock_symbol in const.CRYPTO_CURRENCIES:
        return 1.0

    fd = FundamentalData(key=environ["ALPHA_VANTAGE_API_KEY"])
    data, _ = fd.get_company_overview(reminder.stock_symbol)

    if data["LastSplitDate"] == "None":
        return 1.0
    split_date = datetime.strptime(data["LastSplitDate"], "%Y-%m-%d").date()
    stock_was_split = reminder.created_on < split_date <= date.today()
    if stock_was_split:
        return float(data["LastSplitFactor"][0]) / float(data["LastSplitFactor"][2])
    return 1.0


def get_dividend(reminder):
    if reminder.stock_symbol in const.CRYPTO_CURRENCIES:
        return 0.0

    delta = reminder.remind_on.date() - reminder.created_on
    if delta.days > 90:
        outputsize = "full"
    else:
        outputsize = "compact"
    ts = TimeSeries(key=environ["ALPHA_VANTAGE_API_KEY"])
    data, _ = ts.get_daily_adjusted(reminder.stock_symbol, outputsize=outputsize)
    keys = list(data.keys())
    dividend = 0.0
    for key in keys:
        dividend_date = datetime.strptime(key, "%Y-%m-%d").date()
        if reminder.created_on < dividend_date <= reminder.remind_on.date():
            dividend += float(data[key]["7. dividend amount"])

    return dividend


def calculate_returns(original_price, current_price, dividend):
    return round(
        ((current_price - original_price + dividend) / original_price) * 100, 2
    )


def download_random_gif(tags):
    giphy_api = giphy_client.DefaultApi()
    open(const.GIF_FILE_NAME, "w")
    gif_url = (
        giphy_api.gifs_search_get(
            environ["GIPHY_API_KEY"], random.choice(tags), limit=3, offset=3, fmt="json"
        )
        .data[random.choice(range(3))]
        .images.original.url
    )
    urllib.request.urlretrieve(gif_url, const.GIF_FILE_NAME)


def download_pre_selected_gif(url):
    urllib.request.urlretrieve(url, const.GIF_FILE_NAME)


def remove_file(file):
    os.remove(file) if os.path.exists(file) else None
