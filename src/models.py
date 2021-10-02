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
    InternalError,
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
    short = BooleanField(default=False)
    is_finished = BooleanField(default=False)

    class Meta:
        table_name = "reminders"

    def finish(self):
        self.is_finished = True
        self.save()

    def refresh_from_db(self):
        return Reminder.get_by_id(self.id)

    @classmethod
    def create_instance(cls, values):
        with db.atomic() as transaction:
            try:
                Reminder.create(
                    user_name=values["user_name"],
                    tweet_id=values["tweet_id"],
                    created_on=values["created_on"],
                    remind_on=values["remind_on"],
                    stock_symbol=values["stock_symbol"],
                    stock_price=values["stock_price"],
                    short=values["short"],
                )
            except InternalError:
                transaction.rollback()

    @classmethod
    def due_now(cls):
        return cls.select().where(
            cls.remind_on.between(
                # TODO: I think this should rather fetch all reminders for today's date.
                #  If the job fails, upon retry, the reminder might not be fetched if
                #  it's outside of the 6 min window
                datetime.now() - timedelta(minutes=3),
                datetime.now() + timedelta(minutes=3),
            ),
            cls.is_finished == False,  # noqa
        )


def migrate():
    tables = db.get_tables()
    if [Reminder] not in tables:
        db.create_tables([Reminder])


if __name__ == "__main__":
    migrate()
