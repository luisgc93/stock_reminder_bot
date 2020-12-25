from os import environ

from peewee import (
    BigIntegerField,
    DateField,
    CharField,
    FloatField,
    Model,
)
from playhouse.db_url import connect

# Use default sqlite db in tests
db = connect(environ.get("DATABASE_URL") or "sqlite:///default.db")


class BaseModel(Model):
    class Meta:
        database = db


class Reminder(BaseModel):
    user_name = CharField()
    tweet_id = BigIntegerField()
    created_on = DateField()
    remind_on = DateField()
    stock_symbol = CharField()
    stock_price = FloatField()

    class Meta:
        table_name = "reminders"


def migrate():
    tables = db.get_tables()
    if [Reminder] not in tables:
        db.create_tables([Reminder])


if __name__ == "__main__":
    migrate()
