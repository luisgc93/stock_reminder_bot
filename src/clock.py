from os import environ

import sentry_sdk
from apscheduler.schedulers.blocking import BlockingScheduler

from . import bot, const

sentry_sdk.init(environ["SENTRY_PROJECT_URL"], traces_sample_rate=1.0)
sched = BlockingScheduler()


@sched.scheduled_job("interval", minutes=2)
def timed_job():
    api = bot.init_tweepy()
    api.update_with_media(
        filename=const.MR_SCROOGE_IMAGE_PATH,
        status="TEST" + const.POSITIVE_RETURNS_EMOJI,
        in_reply_to_status_id=1340323379136634880,
    )
    bot.reply_to_mentions()


@sched.scheduled_job("cron", day_of_week="mon-sun", hour=12)
def scheduled_job():
    bot.reply_to_reminders()


def main():
    sched.start()


if __name__ == "__main__":
    main()
