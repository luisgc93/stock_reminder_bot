from os import environ

from peewee import BigIntegerField, Model
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


def migrate():
    db.create_tables([Mention])


if __name__ == "__main__":
    migrate()
