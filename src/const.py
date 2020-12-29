DATE_TIME_STRINGS = ("year", "month", "week", "day", "hour", "minutes", "tomorrow")

CASHTAG = "$"

CRYPTO_CURRENCIES = ("BTC", "ETH", "XRP", "LTC", "NEO", "IOTA")

POSITIVE_RETURNS_EMOJI = "🚀🤑📈"

NEGATIVE_RETURNS_EMOJI = "😭📉"

MR_SCROOGE_IMAGE_PATH = r"images/mr_scrooge.png"

MR_BURNS_IMAGE_PATH = r"images/mr_burns.png"

API_LIMIT_EXCEEDED_ERROR = (
    "Our standard API call frequency is 5 calls per minute and 500 calls per day."
)

INVALID_MENTION_RESPONSE = (
    "To create a reminder, mention me with one or more ticker symbols and a date. "
    'E.g. "Remind me of $BTC in 3 months".'
)

API_LIMIT_EXCEEDED_RESPONSE = (
    "Whoopsies. It looks like my api limit was exceeded. Please try again later "
)

STOCK_NOT_FOUND_RESPONSE = (
    "Sorry, I couldn't find any securities under that ticker 😓. "
    "I only support NASDAQ stocks and a few cryptocurrencies: "
    "https://www.nasdaq.com/market-activity/stocks/screener."
)
