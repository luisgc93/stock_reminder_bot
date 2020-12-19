# stock_reminder bot 🤖 
[![Build Status](https://travis-ci.org/luisgc93/stock_reminder_bot.svg?branch=master)](https://travis-ci.org/luisgc93/stock_reminder_bot) [![codecov](https://codecov.io/gh/luisgc93/stock_reminder_bot/branch/master/graph/badge.svg?token=2sx6C5pkSW)](https://codecov.io/gh/luisgc93/stock_reminder_bot)

A [twitter bot](https://twitter.com/stock_reminder) that registers reminders for stock and cryptocurrency prices.
Mention the bot with a cashtag followed by a stock or cryptocurrency's ticker symbol and the reminder date:

![image](https://user-images.githubusercontent.com/32971373/102701956-09e00480-425d-11eb-8a0e-a38f274db994.png)

The bot will then get back at you on the specified date with your investment results:

![image](https://user-images.githubusercontent.com/32971373/102701977-70fdb900-425d-11eb-9215-a1038dab2a9f.png)

A custom response is returned depending on the outcome:

![image](https://user-images.githubusercontent.com/32971373/102701985-8ffc4b00-425d-11eb-980a-e3a97b45e297.png)


## Implementation 🛠️
The bot uses [RomelTorres' python wrapper](https://github.com/RomelTorres/alpha_vantage) for the [Alpha Vantage API](https://www.alphavantage.co/documentation/). It's deployed on [Heroku with Docker](https://devcenter.heroku.com/articles/build-docker-images-heroku-yml) 🐳 and uses two separate [clock processes](https://devcenter.heroku.com/articles/clock-processes-python) for posting articles and listening to twitter mentions. To avoid duplicate replies, the bot saves the mention's id into a postgres database table which is queried through [peewee](http://docs.peewee-orm.com/en/latest/)'s ORM.

## Usage
Register an account on [Twitter's Developer Platform](https://developer.twitter.com/en) and store your credentials in `/envfiles/local.env`.
To run the bot locally, start the project containers with `make env-start` and then try out the bot's features with:

`make tweet-article`

`make reply-mentions`
 
To run all the tests use:
 
`make test`
