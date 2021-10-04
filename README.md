# stock_reminder bot 🤖 
[![Build Status](https://www.travis-ci.com/luisgc93/stock_reminder_bot.svg?branch=master)](https://www.travis-ci.com/luisgc93/stock_reminder_bot) [![codecov](https://codecov.io/gh/luisgc93/stock_reminder_bot/branch/master/graph/badge.svg?token=2sx6C5pkSW)](https://codecov.io/gh/luisgc93/stock_reminder_bot)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A [twitter bot](https://twitter.com/stock_reminder) that registers reminders for stock and cryptocurrency prices.
Mention the bot with a [cashtag](https://money.cnn.com/2012/07/31/technology/twitter-cashtag/index.htm) followed by a stock or cryptocurrency ticker symbol and the reminder date:

<img width="480" alt="bot_mention" src="https://user-images.githubusercontent.com/32971373/102701956-09e00480-425d-11eb-8a0e-a38f274db994.png">


The bot will then get back to you on the specified date with your investment results and a randomly generated gif that will match your earnings:

<img width="480" alt="bot_mention" src="https://user-images.githubusercontent.com/32971373/103879153-baf8f280-50d7-11eb-9808-846e3263ceb5.png">

<img width="480" alt="bot_mention" src="https://user-images.githubusercontent.com/32971373/103919831-cf0d1600-5110-11eb-80bb-ae50621b143b.png">

Additionally, the bot can also produce rating reports when it is mentioned with a ticker symbol and the words "report" or "analyse"/"analyze":

<img width="460" alt="bot_mention" src="https://user-images.githubusercontent.com/32971373/104827145-2cb10900-585b-11eb-8593-fbb7d5feb659.png">

## Implementation 🛠️
The bot uses [RomelTorres' python wrapper](https://github.com/RomelTorres/alpha_vantage) for the [Alpha Vantage API](https://www.alphavantage.co/documentation/). It's deployed on [Heroku with Docker](https://devcenter.heroku.com/articles/build-docker-images-heroku-yml) 🐳 and uses a [clock process](https://devcenter.heroku.com/articles/clock-processes-python) for replying to twitter mentions and posting reminders. When a mention is in the correct format, a reminder object is saved into a postgres database through [peewee](http://docs.peewee-orm.com/en/latest/)'s ORM. Every 2 minutes, the bot will check whether any reminders are due and publish an update by replying to the initial tweet with the investment results. Further implementation details can be found in the project's [medium post](https://luisgc93.medium.com/building-a-stock-reminder-twitter-bot-with-python-and-alpha-vantage-api-24189566e705).

## Usage
Register an account on [Twitter's Developer Platform](https://developer.twitter.com/en) and store your credentials in `/envfiles/local.env`.
To run the bot locally, start the project containers with `make env-start` and then try out the bot's features with:

`make reply-mentions`
 
To run all the tests use:
 
`make test`

To check code formatting:

`make linting`
