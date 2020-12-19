from os import environ

import sentry_sdk
from apscheduler.schedulers.blocking import BlockingScheduler

from . import bot

sentry_sdk.init(environ["SENTRY_PROJECT_URL"], traces_sample_rate=1.0)
sched = BlockingScheduler()


@sched.scheduled_job("interval", minutes=2)
def timed_job():
    bot.reply_to_mentions()


@sched.scheduled_job("cron", day_of_week="mon-sun", hour=12)
def scheduled_job():
    bot.reply_to_reminders()


def main():
    sched.start()


if __name__ == "__main__":
    main()
