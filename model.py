from datetime import datetime
from peewee import SqliteDatabase, Model, CharField, DateTimeField


db = SqliteDatabase('short_url.db')


class ShortUrl(Model):
    up_date = DateTimeField(default=datetime.now())
    short_url = CharField(unique=True, max_length=5)
    url = CharField(unique=True)

    class Meta:
        database = db
