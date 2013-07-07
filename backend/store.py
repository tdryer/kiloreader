from collections import namedtuple
import sqlite3

# TODO: disadvantage of being immutable: can't imperatively build them
# TODO: pylint can't catch invalid constructions
# TODO: should probably copy more RSS nomenclature
Feed = namedtuple("Feed", "title, feed_url, site_url, fetch_date, id")

class FeedStore(object):

    def __init__(self, db_name):
        """Initialize FeedStore from given db_name."""
        self._db = sqlite3.connect(db_name)
        self._db.execute("""
            CREATE TABLE IF NOT EXISTS feed (
                   title TEXT,
                   feed_url TEXT,
                   site_url TEXT,
                   fetch_date INTEGER,
                   id INTEGER PRIMARY KEY AUTOINCREMENT
            )
        """)

    # TODO ordering here is fragile
    # TODO should be add_feeds
    # TODO: check if feed already exists
    def add_feed(self, title, feed_url, site_url):
        self._db.execute("""
            INSERT INTO feed (
                title,
                feed_url,
                site_url
            ) VALUES (?, ?, ?)
        """, (title, feed_url, site_url)).lastrowid
        self._db.commit()

    def list_feeds(self):
        res = self._db.execute("""
            SELECT
                title,
                feed_url,
                site_url,
                fetch_date,
                id
            FROM feed
        """).fetchall()
        return [Feed(*tup) for tup in res]

    def update_feed_fetch_date(self, feed_id, fetch_date):
        pass
