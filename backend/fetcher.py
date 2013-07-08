"""Fetches feeds from the feed store and downloads entries."""

import argparse
import opml
import feedparser
from time import mktime
from datetime import datetime
from hashlib import sha1

from store import FeedStore, Feed

def opml_import(store, opml_path):
    """Populate feed store with feeds from an OPML file."""
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

def fetch_feeds(store):
    """Check for feeds that need updating and update them."""
    feeds = store.list_feeds()
    for feed in feeds:
        if feed.fetch_date is None:
            print "Feed {} has never been fetched".format(feed.id)
            fetch_feed(store, feed)
        else:
            print "Feed {} is up to date".format(feed.id)

def fetch_feed(store, feed):
    """Fetch the given feed."""
    if raw_input("Fetch {}? ".format(feed.feed_url)).lower() == "y":
        print "Fetching {}...".format(feed.feed_url)
        parsed_feed = feedparser.parse(feed.feed_url)
        print "Found {} entries".format(len(parsed_feed.entries))
        save_parsed_entries(store, feed.id, parsed_feed.entries)
        # TODO: update feed fetch date
    else:
        print "Skipping {}...".format(feed.feed_url)

def save_parsed_entries(store, feed_id, parsed_entries):
    """Adds parsed entries to the FeedStore."""
    for parsed_entry in parsed_entries:
        title = parsed_entry.title if "title" in parsed_entry else "Untitled"
        url = parsed_entry.link if "link" in parsed_entry else None # TODO
        try:
            date = datetime.fromtimestamp(mktime(parsed_entry.published_parsed))
        except AttributeError:
            date = 0 # TODO
        # TODO: make sure content is sanitized
        if hasattr(parsed_entry, "content"):
            content = parsed_entry.content[0]["value"]
        else:
            content = parsed_entry.description
        author = "TODO"
        guid = sha1(parsed_entry.id).hexdigest()
        store.add_entry(feed_id, title, url, author, content, date, guid)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("db_file")
    parser.add_argument("-o", "--opml", type=str)
    args = parser.parse_args()

    print "Loading FeedStore from {}".format(args.db_file)
    store = FeedStore(args.db_file)
    if args.opml:
        opml_import(store, args.opml)
    fetch_feeds(store)

if __name__ == "__main__":
    main()
