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
        feed_id = int(feed_id)
        # TODO: this is test data
        self.write(json.dumps([
                {
                    "id": 1,
                    "feed_id": feed_id,
                    "title": "This is a test",
                    "content": "This is the content of the post.",
                    "read": True
                },
                {
                    "id": 2,
                    "feed_id": feed_id,
                    "title": "Foo bar baz",
                    "content": "This is the content of the second post.",
                    "read": False
                }
        ]))

application = tornado.web.Application([
    (r"/api/feed/?", FeedHandler),
    (r"/api/feed/(?P<feed_id>[0-9]+)/entry/?", EntryHandler),
])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("db_file")
    parser.add_argument("port")
    args = parser.parse_args()

    store = FeedStore(args.db_file)
    application.listen(args.port)
    tornado.ioloop.IOLoop.instance().start()
