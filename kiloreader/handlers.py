import tornado.ioloop
import tornado.web
import json

from kiloreader.models import FeedStore
from kiloreader import tasks

class FeedsHandler(tornado.web.RequestHandler):

    def initialize(self, store, feed_proxy_f):
        self._store = store
        self._feed_proxy_f = feed_proxy_f

    def get(self):
        """Get the list of feeds."""
        feeds = self._store.list_feeds()
        res = [{
            "title": feed["title"],
            "feed_url": feed["feed_url"],
            "site_url": feed["site_url"],
            "id": feed["id"],
            "unread_entries_count": feed["unread_entries_count"],
        } for feed in feeds]
        self.write(json.dumps(res))

    def post(self):
        """Add a new feed."""
        body = json.loads(self.request.body)
        feed_url = body["feed_url"]
        # TODO: given feed_url, get full feed object

        feed = tasks.add_new_feed(self._store, self._feed_proxy_f, feed_url)

        self.set_status(201) # Created
        # TODO: set location header
        self.write(json.dumps(feed))

class FeedHandler(tornado.web.RequestHandler):

    def initialize(self, store):
        self._store = store

    def delete(self, feed_id):
        """Delete a feed."""
        # TODO: handle feed not existing
        self._store.delete_feed(feed_id)
        self.set_status(204) # No content

class EntryHandler(tornado.web.RequestHandler):

    def initialize(self, store):
        self._store = store

    def patch(self, entry_id):
        """Update read status of the entry."""
        # TODO handle entry not existing
        entry = self._store.get_entry(entry_id)
        try:
            body = json.loads(self.request.body)
            is_read = body["is_read"] == True
        except KeyError:
            raise tornado.web.HTTPError(400)
        self._store.update_entry_read(entry_id, is_read)
        entry.update({"is_read": is_read})
        self.write(json.dumps(entry))

class EntriesHandler(tornado.web.RequestHandler):

    def initialize(self, store):
        self._store = store

    def get(self):
        """Get list of entries.

        If there are no entries, or feed does not exist, returns empty list.

        TODO: pagination
        """
        feed = self.get_argument("feed", None)
        feed = int(feed) if feed is not None else None
        is_read = self.get_argument("is_read", None)
        is_read = is_read == "true" if is_read is not None else None
        limit = self.get_argument("limit", None)
        limit = int(limit) if limit is not None else None
        # TODO: remove after_date
        after_date = self.get_argument("after_date", None)
        after_date = int(after_date) if after_date is not None else None

        entries = self._store.list_entries(feed=feed, is_read=is_read,
                                           limit=limit, after_date=after_date)
        res = [{
            "feed_id": entry["feed_id"],
            "title": entry["title"],
            "url": entry["url"],
            "author": entry["author"],
            "content": entry["content"],
            "date": entry["date"],
            "is_read": entry["is_read"],
            "guid": entry["guid"],
            "id": entry["id"],
        } for entry in entries]
        self.write(json.dumps(res))


class RefreshesHandler(tornado.web.RequestHandler):

    def initialize(self, store, feed_proxy_f):
        self._store = store
        self._feed_proxy_f = feed_proxy_f

    def post(self):
        """Create a new refresh."""
        # TODO: blocks the IOLoop
        tasks.refresh_feeds(self._store, self._feed_proxy_f)
        self.set_status(201) # Created
        self.write(json.dumps({"refreshed feeds": 0})) # TODO

def get_routes(store, feed_proxy_f):
    """Return routes for Tornado application."""
    return [

        # show/add subscribed feeds
        (r"/api/feeds/?", FeedsHandler,
         {"store": store, "feed_proxy_f": feed_proxy_f}),

        # unsubscribe feed
        (r"/api/feeds/(?P<feed_id>[0-9]+)/?", FeedHandler, {"store": store}),

        # get list of entries (all or for given feed_id or read status)
        # TODO pagination
        (r"/api/entries/?", EntriesHandler, {"store": store}),

        # modify entry read status
        (r"/api/entries/(?P<entry_id>[0-9]+)/?", EntryHandler,
         {"store": store}),

        # refresh feeds
        (r"/api/refreshes/?", RefreshesHandler,
         {"store": store, "feed_proxy_f": feed_proxy_f}),

    ]
