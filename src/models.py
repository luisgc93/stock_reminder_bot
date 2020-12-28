from datetime import date
from os import environ

from peewee import (
    BigIntegerField,
    DateField,
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
    remind_on = DateField()
    stock_symbol = CharField()
    stock_price = FloatField()
    is_finished = BooleanField(default=False)

    class Meta:
        table_name = "reminders"

    def finish(self):
        self.is_finished = True
        self.save()

    @classmethod
    def due_today(cls):
        return cls.select().where(
            cls.remind_on == date.today(), cls.is_finished == False  # noqa
        )


def migrate():
    db.create_tables([Reminder])


if __name__ == "__main__":
    migrate()
