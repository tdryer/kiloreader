"""Fetches feeds from the feed store and downloads entries."""

import argparse
import opml

from store import FeedStore, Feed

def opml_import(db_file, opml_path):
    store = FeedStore(db_file)

    outlines = opml.parse(opml_path)
    to_parse = [outlines]
    while to_parse:
        outline = to_parse.pop()
        if hasattr(outline, "xmlUrl"):
            feed = Feed(title=outline.title, feed_url=outline.xmlUrl,
                        site_url=outline.htmlUrl, fetch_date=0, id=None)
            print feed
            store.add_feed(outline.title, outline.xmlUrl, outline.htmlUrl)
        for suboutline in outline:
            to_parse.append(suboutline)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("db_file")
    parser.add_argument("opml_path")
    args = parser.parse_args()

    opml_import(args.db_file, args.opml_path)

if __name__ == "__main__":
    main()
