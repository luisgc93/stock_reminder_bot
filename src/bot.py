import os
import random
import re

import giphy_client
import pytz

import urllib.request
import tweepy
from os import environ

from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.foreignexchange import ForeignExchange
from alpha_vantage.fundamentaldata import FundamentalData

from . import const
from .models import Reminder
from dateutil.parser import parse
from datetime import date, datetime
import humanize

import parsedatetime

from PIL import Image, ImageDraw, ImageFont


def init_tweepy():
    auth = tweepy.OAuthHandler(environ["CONSUMER_KEY"], environ["CONSUMER_SECRET"])
    auth.set_access_token(environ["ACCESS_TOKEN"], environ["ACCESS_TOKEN_SECRET"])
    return tweepy.API(auth)


def reply_to_mentions():
    api = init_tweepy()
    new_mentions = api.mentions_timeline(since_id=get_last_replied_tweet_id(api))
    for mention in new_mentions:
        tweet = mention.text
        user = mention.user.screen_name
        if demands_report(tweet):
            stock = parse_stock_symbols(tweet)[0]
            generate_company_report(stock.replace("$", ""))
            media = api.media_upload("report.png")
            api.update_status(
                status=f"@{user} Knowledge is power! Here is your company "
                f"report for {stock}:",
                in_reply_to_status_id=mention.id,
                media_ids=[media.media_id],
            )
            os.remove("report.png") if os.path.exists("report.png") else None
            return
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
            download_random_gif(const.FINGERS_CROSSED_GIF_TAG)
            media = api.media_upload("random.gif")
            api.update_status(
                status=f"@{user} Sure thing buddy! I'll remind you "
                f"of the price of {' '.join(stocks)} on "
                f"{remind_on.strftime('%A %B %d %Y')}. "
                f"I hope you make tons of money! 🤑",
                in_reply_to_status_id=mention.id,
                media_ids=[media.media_id],
            )
            os.remove("random.gif") if os.path.exists("random.gif") else None
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
    for reminder in Reminder.due_now():
        api = init_tweepy()
        split_factor = get_split_factor(reminder)
        dividend = get_dividend(reminder)
        original_adjusted_price = reminder.stock_price / split_factor
        current_price = get_price(reminder.stock_symbol)
        rate_of_return = calculate_returns(
            original_adjusted_price, current_price, dividend
        )
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
        status = (
            f"@{reminder.user_name} {time_since_created_on} ago you bought "
            f"${reminder.stock_symbol} at ${'{:,.2f}'.format(reminder.stock_price)}"
            f"{stock_split_message} It is now worth ${'{:,.2f}'.format(current_price)}"
            f"{dividend_message}. That's a return of {rate_of_return}%! "
        )
        if rate_of_return > 0:
            download_random_gif(const.POSITIVE_RETURN_TAGS)
            emoji = const.POSITIVE_RETURNS_EMOJI
        else:
            download_random_gif(const.NEGATIVE_RETURN_TAGS)
            emoji = const.NEGATIVE_RETURNS_EMOJI

        media = api.media_upload("random.gif")
        api.update_status(
            status=status + emoji,
            media_ids=[media.media_id],
            in_reply_to_status_id=reminder.tweet_id,
        )
        reminder.finish()
        os.remove("random.gif") if os.path.exists("random.gif") else None


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


def demands_report(tweet):
    return any(
        keyword in tweet.lower() for keyword in const.REPORT_KEYWORDS
    ) and contains_stock(tweet)


def generate_company_report(stock):
    fd = FundamentalData(key=environ["ALPHA_VANTAGE_API_KEY"])
    data, _ = fd.get_company_overview(stock)
    for (key, val) in data.items():
        if val.isnumeric():
            data[key] = "${:,.2f}".format(float(val))

    if data["DividendPerShare"] == "None":
        for key in [key for key in data.keys() if "dividend" in key.lower()]:
            data.pop(key)
            data["DividendPerShare"] = "None"

    img = Image.new("RGB", (600, 16 * len(data)), color=(255, 255, 255))

    d = ImageDraw.Draw(img)
    text = "\n\n ".join(
        "{!s}={!s}".format(key, val)
        for (key, val) in data.items()
        if key in const.REPORT_FIELDS
    )

    text = text.replace("=", ": ").replace("'", "")
    font = ImageFont.truetype("fonts/Arimo-Regular.ttf", 14)
    d.text((14, 14), text, font=font, fill=(0, 0, 0))
    img.save("report.png")


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
    open("random.gif", "w")
    gif_url = (
        giphy_api.gifs_search_get(
            environ["GIPHY_API_KEY"], random.choice(tags), limit=3, offset=3, fmt="json"
        )
        .data[random.choice(range(3))]
        .images.original.url
    )
    urllib.request.urlretrieve(gif_url, "random.gif")
