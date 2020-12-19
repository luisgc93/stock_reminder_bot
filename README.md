# stock_reminder bot 🤖 
[![Build Status](https://travis-ci.org/luisgc93/stock_reminder_bot.svg?branch=master)](https://travis-ci.org/luisgc93/stock_reminder_bot) [![codecov](https://codecov.io/gh/luisgc93/stock_reminder_bot/branch/master/graph/badge.svg?token=2sx6C5pkSW)](https://codecov.io/gh/luisgc93/stock_reminder_bot)

A [twitter bot](https://twitter.com/stock_reminder) that registers reminders for stock and cryptocurrency prices.

## Implementation 🛠️
The bot uses [RomelTorres' python wrapper](https://github.com/RomelTorres/alpha_vantage) for the [Alpha Vantage API](https://www.alphavantage.co/documentation/). It's deployed on [Heroku with Docker](https://devcenter.heroku.com/articles/build-docker-images-heroku-yml) 🐳 and uses two separate [clock processes](https://devcenter.heroku.com/articles/clock-processes-python) for posting articles and listening to twitter mentions. To avoid duplicate replies, the bot saves the mention's id into a postgres database table which is queried through [peewee](http://docs.peewee-orm.com/en/latest/)'s ORM.

## Usage
Register an account on [Twitter's Developer Platform](https://developer.twitter.com/en) and store your credentials in `/envfiles/local.env`.
To run the bot locally, start the project containers with `make env-start` and then try out the bot's features with:

`make tweet-article`

`make reply-mentions`
 
To run all the tests use:
 
`make test`
