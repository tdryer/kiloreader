from collections import namedtuple
import sqlite3

# TODO: disadvantage of being immutable: can't imperatively build them
# TODO: pylint can't catch invalid constructions
# TODO: should probably copy more RSS nomenclature
Feed = namedtuple("Feed", "title, feed_url, site_url, fetch_date, id")

Entry = namedtuple("Entry", "feed_id, title, url, author, content, date, is_read, guid, id")

class FeedStore(object):

    def __init__(self, db_name):
        """Initialize FeedStore from given db_name."""
        self._db = sqlite3.connect(db_name)
        self._db.execute("""
            CREATE TABLE IF NOT EXISTS feed (
                   title TEXT NOT NULL,
                   feed_url TEXT NOT NULL,
                   site_url TEXT NOT NULL,
                   fetch_date INTEGER,
                   id INTEGER PRIMARY KEY AUTOINCREMENT
            )
        """)
        # TODO use foreign key?
        # TODO guid + feed_id should be unique
        self._db.execute("""
            CREATE TABLE IF NOT EXISTS entry (
                   feed_id INTEGER NOT NULL,
                   title TEXT NOT NULL,
                   url TEXT NOT NULL,
                   author TEXT NOT NULL,
                   content TEXT NOT NULL,
                   date INTEGER NOT NULL,
                   is_read BOOLEAN NOT NULL,
                   guid TEXT NOT NULL,
                   id INTEGER PRIMARY KEY AUTOINCREMENT
            )
        """)

    # TODO ordering here is fragile
    # TODO should be add_feeds
    # TODO: check if feed already exists
    # TODO: return ID?
    def add_feed(self, title, feed_url, site_url):
        self._db.execute("""
            INSERT INTO feed (
                title,
                feed_url,
                site_url
            ) VALUES (?, ?, ?)
        """, (title, feed_url, site_url)).lastrowid
        self._db.commit()

    # TODO: should be add_entries
    def add_entry(self, feed_id, title, url, author, content, date, guid):
        """Add new entry to a feed.

        If the feed already has the entry with the same guid, that entry is
        replaced.
        """
        is_read = False
        self._db.execute("""
            DELETE FROM entry WHERE feed_id = ? AND guid = ?
        """, (feed_id, guid))
        self._db.execute("""
            INSERT INTO entry (
                feed_id,
                title,
                url,
                author,
                content,
                date,
                is_read,
                guid
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (feed_id, title, url, author, content, date, is_read, guid))
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

    def is_feed_id(self, feed_id):
        """Return True if feed with this ID exists."""
        res = self._db.execute("""
            SELECT
                count()
            FROM feed
            WHERE id = ?
        """, (feed_id,)).fetchone()
        return res[0] == 1

    # TODO: needs start_after as well as count
    # TODO: needs to sort by date
    def list_entries(self, feed_id, count):
        """Return at most count newest entries from feed

        Returns None if feed doesn't exist.
        """
        if not self.is_feed_id(feed_id):
            return None
        res = self._db.execute("""
            SELECT
                feed_id,
                title,
                url,
                author,
                content,
                date,
                is_read,
                guid,
                id
            FROM entry
            WHERE feed_id = ?
        """, (feed_id,)).fetchall()
        # TODO restrict count
        # TODO is_read is an integer instead of bool
        return [Entry(*tup) for tup in res]

    def update_entry_read(self, entry_id, is_read):
        """Update the read status of an entry."""
        # TODO handle entry_id not existing
        print "setting entry {} to {}".format(entry_id, is_read)
        res = self._db.execute("""
            UPDATE entry
            SET is_read = ?
            WHERE id = ?
        """, (is_read, entry_id))
        self._db.commit()
