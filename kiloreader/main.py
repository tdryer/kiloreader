import tornado
import argparse
import time

from kiloreader.models import FeedStore
from kiloreader import handlers

def get_app(db_file=None, time_f=(lambda: int(time.time())),
            feed_proxy_f=lambda url: url):
    """Return Tornado application instance.

    This is used by main() to start the application, and by functional tests
    for testing. The default dependencies should be those for the real
    application.

    If db_file is None, use an in-memory DB.
    """
    store = FeedStore(db_file, time_f)
    return tornado.web.Application(handlers.get_routes(store, feed_proxy_f))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("db_file")
    parser.add_argument("port")
    args = parser.parse_args()

    application = get_app(db_file=args.db_file)

    #store = FeedStore(args.db_file)

    #application = tornado.web.Application(handlers.get_routes(store))
    application.listen(args.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
