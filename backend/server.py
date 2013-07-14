"""Feed API server."""

import tornado.ioloop
import tornado.web
import json
import argparse

from store import FeedStore, Feed

class FeedHandler(tornado.web.RequestHandler):
    def get(self):
        feeds = store.list_feeds()
        res = [{
            "title": feed.title,
            "feed_url": feed.feed_url,
            "site_url": feed.site_url,
            "id": feed.id,
        } for feed in feeds]
        self.write(json.dumps(res))

class EntryHandler(tornado.web.RequestHandler):
    def get(self, feed_id):
        entries = store.list_entries(int(feed_id), 10)
        if entries is None:
            # TODO: should return json errors?
            raise tornado.web.HTTPError(404, "Feed does not exist")
        else:
            res = [{
                "feed_id": entry.feed_id,
                "title": entry.title,
                "url": entry.url,
                "author": entry.author,
                "content": entry.content,
                "date": entry.date,
                "is_read": entry.is_read,
                "guid": entry.guid,
                "id": entry.id,
            } for entry in entries]
            self.write(json.dumps(res))

class EntryHandler2(tornado.web.RequestHandler):
    def put(self, entry_id):
        """Update read status of the entry."""
        # TODO check that entry exists
        try:
            body = json.loads(self.request.body)
            is_read = body["is_read"] == True
        except KeyError:
            raise tornado.web.HTTPError(400)
        store.update_entry_read(entry_id, is_read)

application = tornado.web.Application([
    (r"/api/feed/?", FeedHandler),
    (r"/api/feed/(?P<feed_id>[0-9]+)/entry/?", EntryHandler),

    # list all/read/unread entries from all or one feeds
    #(r"/api/entries/?", EntriesHandler),
    # mark an entry as read/unread
    (r"/api/entries/(?P<entry_id>[0-9]+)/?", EntryHandler2),
])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("db_file")
    parser.add_argument("port")
    args = parser.parse_args()

    store = FeedStore(args.db_file)
    application.listen(args.port)
    tornado.ioloop.IOLoop.instance().start()
