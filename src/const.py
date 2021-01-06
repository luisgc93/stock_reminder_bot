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

POSITIVE_RETURNS_EMOJI = "🚀🤑📈"

NEGATIVE_RETURNS_EMOJI = "😭📉"

FINGERS_CROSSED_GIF_TAG = ["fingers crossed"]

GIF_FILE_NAME = "random.gif"

POSITIVE_RETURN_TAGS = ["money", "rich", "cash", "dollars"]

NEGATIVE_RETURN_TAGS = ["poor", "broke", "no money"]

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

API_LIMIT_EXCEEDED_ERROR = (
    "Our standard API call frequency is 5 calls per minute and 500 calls per day."
)

INVALID_MENTION_RESPONSE = (
    "To create a reminder, mention me with one or more ticker "
    "symbols and a date. E.g. 'Remind me of $BTC in 3 months'. "
    "If you'd like me to analyse a company for you, mention me "
    "with the words 'analyse' or 'report' plus the company's "
    "ticker symbol. E.g. 'Analyse $AMZN'."
)

API_LIMIT_EXCEEDED_RESPONSE = (
    "Whoopsies. It looks like my api limit was exceeded. Please try again later "
)

STOCK_NOT_FOUND_RESPONSE = (
    "Sorry, I couldn't find any securities under that ticker 😓. "
    "I only support NASDAQ stocks and a few cryptocurrencies: "
    "https://www.nasdaq.com/market-activity/stocks/screener."
)
