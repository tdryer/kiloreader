import time
import sqlalchemy
from sqlalchemy import (Table, Column, Integer, String, Boolean, MetaData,
                        ForeignKey, sql, func)

class FeedStore(object):

    def __init__(self, db_name, time_f):
        """Initialize FeedStore from given db_name."""
        self._time_f = time_f
        uri = ("sqlite:///:memory:" if db_name is None
               else "sqlite:///{}".format(db_name))
        engine = sqlalchemy.create_engine(uri, echo=False)
        metadata = MetaData()
        self._feed_table = Table('feeds', metadata,
            Column("title", String, nullable=False),
            Column("feed_url", String, nullable=False),
            Column("site_url", String, nullable=False),
            Column("fetch_date", Integer, nullable=False),
            Column("id", Integer, primary_key=True),
        )
        self._entry_table = Table('entries', metadata,
            Column("feed_id", Integer, ForeignKey("feeds.id"), nullable=False),
            Column("title", String, nullable=False),
            Column("url", String, nullable=False),
            Column("author", String, nullable=False),
            Column("content", String, nullable=False),
            Column("date", Integer, nullable=False),
            Column("is_read", Boolean, nullable=False),
            Column("guid", String, nullable=False),
            Column("id", Integer, primary_key=True),
        )
        metadata.create_all(engine)
        self._conn = engine.connect()

    def get_time(self):
        """Return time value suitable for feed or entry."""
        return self._time_f()

    def add_feed(self, feed):
        """Add new feed and return new id."""
        res = self._conn.execute(self._feed_table.insert(), feed)
        return res.lastrowid

    def delete_feed(self, feed_id):
        """Delete a feed and associated entries."""
        delete_entries = sql.delete(self._entry_table)
        delete_entries = delete_entries.where(
            self._entry_table.c.feed_id == feed_id)
        self._conn.execute(delete_entries)
        delete_feed = sql.delete(self._feed_table)
        delete_feed = delete_feed.where(self._feed_table.c.id == feed_id)
        self._conn.execute(delete_feed)

    def list_feeds(self):
        """Return list of feeds with number of unread entries."""
        select = sql.select([self._feed_table])
        feeds = self._conn.execute(select)
        res = []
        for feed in feeds:
            select_count = sql.select([func.count(self._entry_table)])
            select_count = select_count.where(
                self._entry_table.c.feed_id == feed["id"])
            select_count = select_count.where(
                self._entry_table.c.is_read == False)
            unread_entries_count = self._conn.execute(select_count).fetchone()[0]
            res.append({
                "title": feed.title,
                "feed_url": feed.feed_url,
                "site_url": feed.site_url,
                "fetch_date": feed.fetch_date,
                "id": feed.id,
                "unread_entries_count": unread_entries_count,
            })
        return res

    # TODO: not using plural
    def add_entries(self, entry_list):
        # TODO overwrite entry with same guid
        # allow is_read to be optional
        for entry in entry_list:
            entry["is_read"] = entry.get("is_read", False)
        self._conn.execute(self._entry_table.insert(), entry_list)

    # TODO: reimplement using update_entry
    def update_entry_read(self, entry_id, is_read):
        """Update the read state of an entry."""
        update = sql.update(self._entry_table)
        update = update.where(self._entry_table.c.id == entry_id)
        update = update.values(is_read=is_read)
        self._conn.execute(update)

    def update_entry(self, entry_id, entry):
        """Update an entry.

        Entry can be a partial entry to only update some fields.
        """
        for key in ["feed_id"]:
            if key in entry:
                del entry[key]
        update = sql.update(self._entry_table)
        update = update.where(self._entry_table.c.id == entry_id)
        update = update.values(entry)
        self._conn.execute(update)

    def list_entries(self, feed=None, is_read=None, limit=None,
                     after_date=None):
        """Return list of entries."""
        select = sql.select([self._entry_table])
        # oldest entries first
        select = select.order_by(self._entry_table.c.date.desc())
        # TODO: if statements not necessary?
        if feed is not None:
            select = select.where(self._entry_table.c.feed_id == feed)
        if is_read is True:
            select = select.where(self._entry_table.c.is_read == True)
        if is_read is False:
            select = select.where(self._entry_table.c.is_read == False)
        if limit is not None:
            select = select.limit(limit)
        # TODO: remove after_date
        if after_date is not None:
            # TODO: what if there are entries with the same time?
            select = select.where(self._entry_table.c.date > after_date)
        res = self._conn.execute(select)
        return [dict(entry) for entry in res]

    def get_entry(self, entry_id):
        """Return an entry by ID."""
        select = sql.select([self._entry_table])
        select = select.where(self._entry_table.c.id == entry_id)
        res = self._conn.execute(select)
        return dict(list(res)[0])

    def entry_guid_exists(self, feed_id, guid):
        """Return entry ID if entry with that guid already exists."""
        # TODO: guid should be unique for all feeds
        select = sql.select([self._entry_table])
        select = select.where(self._entry_table.c.feed_id == feed_id)
        select = select.where(self._entry_table.c.guid == guid)
        # TODO: probably better way to do this
        res = self._conn.execute(select).fetchone()
        return None if res is None else res["id"]
