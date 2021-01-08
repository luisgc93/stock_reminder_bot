DATE_TIME_STRINGS = ("year", "month", "week", "day", "hour", "minutes", "tomorrow")

CASHTAG = "$"

CRYPTO_CURRENCIES = (
    "BTC",
    "ETH",
    "XRP",
    "LTC",
    "NEO",
    "EOS",
    "BNB",
    "HT",
    "LINK",
    "BCH",
    "TRX",
    "XTZ",
)

NASDAQ_TRADING_HOURS = ["09:30:00", "16:00:00"]

WEEKEND_DAYS = [5, 6]

POSITIVE_RETURNS_EMOJI = "🚀🤑📈"

NEGATIVE_RETURNS_EMOJI = "😭📉"

FINGERS_CROSSED_GIF_TAG = ["fingers crossed"]

GIF_FILE_NAME = "random.gif"

POSITIVE_RETURN_TAGS = ["money", "rich", "cash", "dollars"]

NEGATIVE_RETURN_GIFS = [
    "https://media.giphy.com/media/3orieUs03VUeeBa7Wo/giphy.gif",
    "https://media.giphy.com/media/l2JdWPIgVK83qxB4Y/giphy.gif",
    "https://media.giphy.com/media/ToMjGppB1bJC04ESjyE/giphy.gif",
    "https://media.giphy.com/media/3orieVe5VYqTdT16qk/giphy.gif"
    "https://media.giphy.com/media/S3n6idriKtiFbZyqve/giphy.gif",
    "https://media.giphy.com/media/qBykyt7AiTOgM/giphy.gif",
    "https://media.giphy.com/media/xThtatVgZVprKd3UEU/giphy.gif",
]

REPORT_KEYWORDS = ["report", "analyse", "analyze"]

REPORT_FIELDS = [
    "Name",
    "Industry",
    "MarketCapitalization",
    "EBITDA",
    "EVToEBITDA",
    "PERatio",
    "PriceToBookRatio",
    "ReturnOnEquityTTM",
    "PEGRatio",
    "Beta",
    "BookValue",
    "DividendPerShare",
    "DividendYield",
    "EPS",
    "DilutedEPSTTM",
    "RevenuePerShareTTM",
    "ProfitMargin",
    "TrailingPE",
    "52WeekHigh",
    "52WeekLow",
    "ForwardAnnualDividendRate",
    "ForwardAnnualDividendYield",
    "PayoutRatio",
    "DividendDate",
    "ExDividendDate",
    "LastSplitFactor",
    "LastSplitDate",
]

REPORT_FONT_PATH = "fonts/Arimo-Regular.ttf"

REPORT_FONT_COLOR = (0, 0, 0)

REPORT_BACKGROUND_COLOR = (255, 255, 255)

REPORT_FILE_NAME = "report.png"

REPORT_RESPONSE = "Knowledge is power! 🧠💪 Here is your company report for $"

CRYPTO_REPORT_RESPONSE = (
    "Knowledge is power! 🧠💪 Here is your crypto ratings report for $"
)

FMP_API_RATING_ENDPOINT = "https://financialmodelingprep.com/api/v3/company/rating/"

FMP_API_GET_PRICE_ENDPOINT = "https://financialmodelingprep.com/api/v3/quote/"

API_LIMIT_EXCEEDED_ERROR = (
    "Our standard API call frequency is 5 calls per minute and 500 calls per day."
)

HELP_MESSAGE = (
    "To create a reminder, mention me with one or more ticker "
    "symbols and a date. E.g. 'Remind me of $BTC in 3 months'. "
    "If you'd like me to analyse a company for you, mention me "
    "with the words 'analyse'/'analyze' or 'report' plus the "
    "company's ticker symbol. E.g. 'Analyse $AMZN'."
)

API_LIMIT_EXCEEDED_RESPONSE = (
    "Whoopsies. It looks like my api limit was exceeded. Please try again later "
)

STOCK_NOT_FOUND_RESPONSE = (
    "Sorry, I couldn't find any securities under that ticker 😓. "
    "I only support NASDAQ stocks and a few cryptocurrencies: "
    "https://www.nasdaq.com/market-activity/stocks/screener."
)
