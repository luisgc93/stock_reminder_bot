from os import environ

from peewee import *
from playhouse.db_url import connect

# Use default sqlite db in tests
db = connect(environ.get("DATABASE_URL") or "sqlite:///default.db")


class BaseModel(Model):
    class Meta:
        database = db


class Mention(BaseModel):
    tweet_id = BigIntegerField()

    class Meta:
        table_name = "mentions"


class Reminder(BaseModel):
    tweet_id = BigIntegerField()
    published_at = DateField()
    reminder_date = DateTimeField()
    stock_symbol = CharField()
    stock_price = FloatField()

    class Meta:
        table_name = "reminders"


def migrate():
    tables = db.get_tables()
    if not tables:
        db.create_tables([Mention, Reminder])


if __name__ == "__main__":
    migrate()
