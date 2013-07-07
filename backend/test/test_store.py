import unittest
import os

import store

class DBTestCase(unittest.TestCase):
    """Test case that initializes temporary DB."""

    TEST_DB = "test.db"

    def setUp(self):
        self.store = store.FeedStore(self.TEST_DB)

    def tearDown(self):
        os.remove(self.TEST_DB)

class DBTest(DBTestCase):

    def test_list_no_feeds(self):
        self.assertEqual(self.store.list_feeds(), [])

    def test_add_and_list_new_feed(self):
        self.store.add_feed("Test", "http://example.com/feed.rss",
                            "http://example.com/")
        feeds = self.store.list_feeds()
        self.assertEqual(len(feeds), 1)
        self.assertEqual(feeds[0].title, "Test")
        self.assertEqual(feeds[0].site_url, "http://example.com/")
        self.assertEqual(feeds[0].feed_url, "http://example.com/feed.rss")

    #def test_get_nonexistent_feed(self):
    #    self.assertIsNone(feeds.Feed.get(self.test_db, 1337))
