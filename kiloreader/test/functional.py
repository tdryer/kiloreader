import unittest
import json
from tornado.testing import AsyncHTTPTestCase
from os import path

from kiloreader import main

TEST_DIR = path.join(path.dirname(__file__), "test_data")

class APITestCase(AsyncHTTPTestCase):
    """End-to-end test for the API."""

    def setUp(self):
        super(APITestCase, self).setUp()
        self._time = 0

    def get_app(self):
        # use in-memory DB and set time to 0
        self._time = 0
        return main.get_app(time_f=lambda: self._time,
                            feed_proxy_f=self._feed_url_proxy)

    def _feed_url_proxy(self, feed_url):
        """Given http feed url, return file url in test directory.

        Filename includes current test time.
        """
        extension = feed_url.split(".")[-1]
        root = ".".join(feed_url.split(".")[:-1])
        filename = "{}.{}.{}".format(root.replace("/", "_"), self._time,
                                     extension)
        file_path = path.join(TEST_DIR, filename)
        if not path.exists(file_path):
            raise ValueError("Cannot proxy '{}': '{}' does not exist."
                             .format(feed_url, file_path))
        return "file://{}".format(file_path)

    def _request(self, url, code=200, method="GET", body=None):
        """Make API request with JSON input and output."""
        body = json.dumps(body) if body is not None else None
        self.http_client.fetch(self.get_url(url), method=method, body=body,
                               callback=self.stop)
        response = self.wait()
        self.assertEqual(response.code, code)
        try:
            return json.loads(response.body)
        except ValueError:
            return response.body

    # an RSS 2.0 example
    TEST_RSS = "http://example.com/test.rss"

class NoFeedsTestCase(APITestCase):
    """Test case where no feeds have been added yet."""

    def _add_test_feed(self):
        """Shortcut to add a test feed and return result."""
        res = self._request("/api/feeds", code=201, method="POST", body={
            "feed_url": self.TEST_RSS,
        })
        return res

    def test_refresh_no_changes(self):
        # add feed
        self._add_test_feed()
        # refresh feeds
        self._request("/api/refreshes", code=201, method="POST", body={})
        # assert there are the same number of entries
        entries = self._request("/api/entries")
        self.assertEqual(len(entries), 4)

    def test_refresh_adds_new_entry(self):
        # add feed
        self._add_test_feed()
        # move time forward
        self._time = 1
        # refresh feeds
        self._request("/api/refreshes", code=201, method="POST", body={})
        # assert there is a new entry
        entries = self._request("/api/entries")
        self.assertEqual(len(entries), 5)
        self.assertEqual(entries[0]["title"], "A new post")

    def test_refresh_updates_entry(self):
        self._time = 1
        self._add_test_feed()
        entries = self._request("/api/entries")
        self.assertEqual(entries[0]["title"], "A new post")
        self._time = 2
        self._request("/api/refreshes", code=201, method="POST", body={})
        entries = self._request("/api/entries")
        self.assertEqual(len(entries), 5)
        self.assertEqual(entries[0]["title"], "A new post (updated)")

    def test_feed_list_unread_count(self):
        self._add_test_feed()
        self.assertEqual(
            self._request("/api/feeds")[0]["unread_entries_count"], 4)
        # mark entry 1 as read
        self._request("/api/entries/1", code=200, method="PATCH", body={
            "is_read": True,
        })
        self.assertEqual(
            self._request("/api/feeds")[0]["unread_entries_count"], 3)

    def test_list_entries_limit(self):
        self._add_test_feed()

        entries = self._request("/api/entries")
        self.assertEqual(len(entries), 4)

        entries = self._request("/api/entries?limit=2")
        self.assertEqual(len(entries), 2)

    def test_newest_entries_first(self):
        self._add_test_feed()
        entries = self._request("/api/entries")
        dates = [e["date"] for e in entries]
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_get_feeds_empty(self):
        self.assertEqual(self._request("/api/feeds"), [])

    # TODO: break this up into separate tests
    def test_add_feed(self):
        # adding new feed returns the new feed
        res = self._request("/api/feeds", code=201, method="POST", body={
            "feed_url": self.TEST_RSS,
        })
        self.assertEqual(res, {
            u"feed_url": unicode(self.TEST_RSS),
            u"fetch_date": 0,
            u"site_url": u"http://liftoff.msfc.nasa.gov/",
            u"title": u"Liftoff News",
            u"id": 1,
        })

        # new feed appears in feed list
        feeds = self._request("/api/feeds")
        self.assertEqual(feeds, [{
            "feed_url": self.TEST_RSS,
            "id": 1,
            "site_url": "http://liftoff.msfc.nasa.gov/",
            "title": "Liftoff News",
            "unread_entries_count": 4,
        }])

        # returns all entries
        entries = self._request("/api/entries")
        self.assertEqual(len(entries), 4)
        self.assertEqual(entries[0]["title"], "Star City")
        # TODO

        # returns all entries if filtering by feed ID
        entries = self._request("/api/entries?feed=1")
        self.assertEqual(len(entries), 4)
        self.assertEqual(entries[0]["title"], "Star City")

        # returns empty list if feed ID does not exist
        entries = self._request("/api/entries?feed=2")
        self.assertEqual(len(entries), 0)

        # returns all entries if filtering by read state false
        entries = self._request("/api/entries?is_read=false")
        self.assertEqual(len(entries), 4)
        self.assertEqual(entries[0]["title"], "Star City")

        # returns empty list if filtering by read state true
        entries = self._request("/api/entries?is_read=true")
        self.assertEqual(len(entries), 0)

        # mark entry 1 as read
        entry = self._request("/api/entries/1", code=200, method="PATCH",
                              body={
            "is_read": True,
        })
        self.assertEqual(entry["title"], "Star City")
        self.assertEqual(entry["is_read"], True)
        entries = self._request("/api/entries?is_read=false")
        self.assertEqual(len(entries), 3)

        # mark entry 1 as unread
        entry = self._request("/api/entries/1", code=200, method="PATCH",
                              body={
            "is_read": False,
        })
        self.assertEqual(entry["title"], "Star City")
        self.assertEqual(entry["is_read"], False)
        entries = self._request("/api/entries?is_read=false")
        self.assertEqual(len(entries), 4)

        # unsubscribe from a feed
        res = self._request("/api/feeds/1", code=204, method="DELETE")
        self.assertEqual(res, "")
        feeds = self._request("/api/feeds")
        self.assertEqual(feeds, [])
        entries = self._request("/api/entries")
        self.assertEqual(entries, [])


if __name__ == "__main__":
    unittest.main()
