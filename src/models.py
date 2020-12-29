from datetime import datetime, timedelta
from os import environ

from peewee import (
    BigIntegerField,
    DateField,
    DateTimeField,
    CharField,
    FloatField,
    Model,
    BooleanField,
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
    remind_on = DateTimeField()
    stock_symbol = CharField()
    stock_price = FloatField()
    is_finished = BooleanField(default=False)

    class Meta:
        table_name = "reminders"

    def finish(self):
        self.is_finished = True
        self.save()

    @classmethod
    def is_due(cls):
        upper = datetime.now() + timedelta(minutes=5)
        lower = datetime.now() - timedelta(minutes=5)

        return cls.select().where(
            lower <= cls.remind_on <= upper,
            cls.is_finished == False,  # noqa
        )


def migrate():
    tables = db.get_tables()
    if [Reminder] not in tables:
        db.create_tables([Reminder])


if __name__ == "__main__":
    migrate()
