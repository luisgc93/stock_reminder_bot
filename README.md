# stock_reminder bot 🤖 
[![Build Status](https://travis-ci.org/luisgc93/stock_reminder_bot.svg?branch=master)](https://travis-ci.org/luisgc93/stock_reminder_bot) [![codecov](https://codecov.io/gh/luisgc93/stock_reminder_bot/branch/master/graph/badge.svg?token=2sx6C5pkSW)](https://codecov.io/gh/luisgc93/stock_reminder_bot)

A [twitter bot](https://twitter.com/stock_reminder) that registers reminders for stock and cryptocurrency prices.
Mention the bot with a [cashtag](https://money.cnn.com/2012/07/31/technology/twitter-cashtag/index.htm) followed by a stock or cryptocurrency ticker symbol and the reminder date:

<img width="480" alt="bot_mention" src="https://user-images.githubusercontent.com/32971373/102701956-09e00480-425d-11eb-8a0e-a38f274db994.png">


The bot will then get back to you on the specified date with your investment results:

<img width="480" alt="bot_mention" src="https://user-images.githubusercontent.com/32971373/102720078-4ad62880-42f2-11eb-942c-9de18e395dc1.png">

<img width="480" alt="bot_mention" src="https://user-images.githubusercontent.com/32971373/102701985-8ffc4b00-425d-11eb-980a-e3a97b45e297.png">

## Implementation 🛠️
The bot uses [RomelTorres' python wrapper](https://github.com/RomelTorres/alpha_vantage) for the [Alpha Vantage API](https://www.alphavantage.co/documentation/). It's deployed on [Heroku with Docker](https://devcenter.heroku.com/articles/build-docker-images-heroku-yml) 🐳 and uses two separate [clock processes](https://devcenter.heroku.com/articles/clock-processes-python) for replying to twitter mentions and posting reminders. When a mention is in the correct format, a reminder object is saved into a postgres database through [peewee](http://docs.peewee-orm.com/en/latest/)'s ORM. Every day at midday UTC, the bot will check whether any reminders are due and publish an update by replying to the initial tweet with the investment results. Further implementation details can be found in the project's [medium post](https://luisgc93.medium.com/building-a-stock-reminder-twitter-bot-with-python-and-alpha-vantage-api-24189566e705).

## Usage
Register an account on [Twitter's Developer Platform](https://developer.twitter.com/en) and store your credentials in `/envfiles/local.env`.
To run the bot locally, start the project containers with `make env-start` and then try out the bot's features with:

`make reply-mentions`
 
To run all the tests use:
 
`make test`
