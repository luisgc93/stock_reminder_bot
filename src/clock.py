from os import environ

import sentry_sdk
from apscheduler.schedulers.blocking import BlockingScheduler

from . import bot

sched = BlockingScheduler()


# @sched.scheduled_job("interval", minutes=2)
# def timed_job():
#     bot.reply_to_mentions()


def main():
    sched.start()


if __name__ == "__main__":
    main()
