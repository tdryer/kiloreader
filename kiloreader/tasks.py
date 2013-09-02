"""Feed parsing tasks."""

import feedparser
from bs4 import BeautifulSoup
from time import mktime
from hashlib import sha1

def add_new_feed(store, feed_proxy_f, feed_url):
    """Fetch the feed_url and add it as a new feed."""
    parsed_feed = _fetch_feed_url(feed_proxy_f, feed_url)
    feed = {
        "feed_url": feed_url,
        "title": parsed_feed.feed.title,
        #"id": -1,
        "fetch_date": store.get_time(),
        "site_url": parsed_feed.feed.link,
    }
    feed_id = store.add_feed(feed)
    feed["id"] = feed_id

    _save_parsed_entries(store, feed_id, parsed_feed.entries)

    return feed

def _fetch_feed_url(feed_proxy_f, feed_url):
    """Fetch feed url and return return feedparser object.

    Raises ValueError if feed can not be parsed.
    """
    # TODO: this can be made more efficient by passing stored etag/modified
    parsed_feed = feedparser.parse(feed_proxy_f(feed_url))
    if parsed_feed.bozo:
        raise ValueError("Can't parse feed: {}"
                         .format(parsed_feed.bozo_exception))
    return parsed_feed

def refresh_feeds(store, feed_proxy_f):
    for feed in store.list_feeds():
        refresh_feed(store, feed_proxy_f, feed["id"], feed["feed_url"])

def refresh_feed(store, feed_proxy_f, feed_id, feed_url):
    parsed_feed = _fetch_feed_url(feed_proxy_f, feed_url)
    _save_parsed_entries(store, feed_id, parsed_feed.entries)

def _add_or_update_entry(store, feed_id, entry):
    """Add entry if new, update if old and something changed."""
    entry_id = store.entry_guid_exists(feed_id, entry["guid"])
    if entry_id is not None:
        # TODO: entry already exists, update it
        store.update_entry(entry_id, entry)
    else:
        # entry is new, add it
        store.add_entries([entry]) # TODO: don't need plural

def _save_parsed_entries(store, feed_id, parsed_entries):
    """Adds parsed entries to the FeedStore."""
    entries = []
    for parsed_entry in parsed_entries:
        title = parsed_entry.title if "title" in parsed_entry else "Untitled"
        url = parsed_entry.link if "link" in parsed_entry else None # TODO
        try:
            # TODO: check that this deals with timezones properly
            date = int(mktime(parsed_entry.published_parsed))
        except AttributeError:
            date = 0 # TODO
        # TODO: make sure content is sanitized
        if hasattr(parsed_entry, "content"):
            content = parsed_entry.content[0]["value"]
        else:
            content = parsed_entry.description
        content = _set_target_blank(content)
        author = "TODO"
        guid = sha1(parsed_entry.id).hexdigest()
        entries.append({
            "feed_id": feed_id,
            "title": title,
            "url": url,
            "author": author,
            "content": content,
            "date": date,
            "guid": guid
        })
    #store.add_entries(entries)
    for entry in entries:
        _add_or_update_entry(store, feed_id, entry)

def _set_target_blank(html):
    """Given fragment of html, set target=_blank attribute on all anchors."""
    soup = BeautifulSoup(html, "lxml")
    for anchor in soup.findAll("a"):
        anchor.attrs["target"] = "_blank"
    return soup.body.decode_contents()
