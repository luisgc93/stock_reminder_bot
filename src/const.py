TW_CHAR_LIMIT = 280

SHORTENED_URL_LENGTH = 23

TRUNCATED_TEXT_STRING = "(...) "

MAX_TRUNCATED_CHARACTER_COUNT = (
    TW_CHAR_LIMIT - SHORTENED_URL_LENGTH - len(TRUNCATED_TEXT_STRING)
)


DATE_TIME_STRINGS = ["year", "month", "week", "day", "hour", "minutes", "tomorrow"]

CASHTAG = "$"


POSITIVE_RETURNS_EMOJI = "🚀🤑📈"

NEGATIVE_RETURNS_EMOJI = "😭📉"

API_LIMIT_EXCEEDED_MESSAGE = (
    "Our standard API call frequency is 5 calls per minute and 500 calls per day."
)

API_LIMIT_EXCEEDED_RESPONSE = (
    "Se ha excedido el límite de búsquedas (5/minuto y 500/día). "
    "Vuelve a probar más tarde."
)

STOCK_NOT_FOUND_MESSAGE = (
    "Invalid API call. Please retry or visit the documentation "
    "(https://www.alphavantage.co/documentation/) for TIME_SERIES_INTRADAY."
)

STOCK_NOT_FOUND_RESPONSE = (
    "Sorry, I can only find stocks that are traded on the NASDAQ 😓: "
    "https://www.nasdaq.com/market-activity/stocks/screener."
)
