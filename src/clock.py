from os import environ

import sentry_sdk
from apscheduler.schedulers.blocking import BlockingScheduler

from . import bot

sentry_sdk.init(environ["SENTRY_PROJECT_URL"], traces_sample_rate=1.0)
sched = BlockingScheduler()


@sched.scheduled_job("interval", minutes=2)
def timed_job():
    a = 1/0
    bot.reply_to_mentions()


def main():
    sched.start()


if __name__ == "__main__":
    main()
