import unittest
import os

import store

class DBTestCase(unittest.TestCase):
    """Test case that initializes temporary DB."""

    TEST_DB = "test1234.db"

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

    def test_add_and_list_new_entry(self):
        self.store.add_feed("Test", "http://example.com/feed.rss",
                            "http://example.com/")
        self.store.add_entry(1, "Test Entry", "http://example.com/test", "Tom",
                             "This is a test entry.", 0, "test_entry")
        entries = self.store.list_entries(1, 10)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].title, "Test Entry")
        self.assertEqual(entries[0].url, "http://example.com/test")
        self.assertEqual(entries[0].author, "Tom")
        self.assertEqual(entries[0].content, "This is a test entry.")
        self.assertEqual(entries[0].date, 0)
        self.assertEqual(entries[0].is_read, False)
        #self.assertIsInstance(entries[0].is_read, bool)
        self.assertEqual(entries[0].guid, "test_entry")

    def test_update_entry_read(self):
        self.store.add_feed("Test", "http://example.com/feed.rss",
                            "http://example.com/")
        self.store.add_entry(1, "Test Entry", "http://example.com/test", "Tom",
                             "This is a test entry.", 0, "test_entry")
        entries = self.store.list_entries(1, 10)
        self.assertFalse(entries[0].is_read)
        self.store.update_entry_read(entries[0].id, True)
        entries = self.store.list_entries(1, 10)
        self.assertTrue(entries[0].is_read)
        self.store.update_entry_read(entries[0].id, False)
        entries = self.store.list_entries(1, 10)
        self.assertFalse(entries[0].is_read)

    def test_add_two_entries_different_guid(self):
        self.store.add_feed("Test", "http://example.com/feed.rss",
                            "http://example.com/")
        self.store.add_entry(1, "Test Entry", "http://example.com/test", "Tom",
                             "This is a test entry.", 0, "test_entry")
        self.store.add_entry(1, "Test Entry 2", "http://example.com/test", "Tom",
                             "This is a test entry.", 0, "test_entry_2")
        entries = self.store.list_entries(1, 10)
        self.assertEqual(len(entries), 2)

    def test_add_two_entries_same_guid(self):
        self.store.add_feed("Test", "http://example.com/feed.rss",
                            "http://example.com/")
        self.store.add_entry(1, "Test Entry", "http://example.com/test", "Tom",
                             "This is a test entry.", 0, "test_entry")
        self.store.add_entry(1, "Test Entry 2", "http://example.com/test", "Tom",
                             "This is a test entry.", 0, "test_entry")
        entries = self.store.list_entries(1, 10)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].title, "Test Entry 2")

    def test_list_entries_nonexistent_feed(self):
        self.assertEqual(self.store.list_entries(1, 10), None)

    def test_list_entries_no_entries(self):
        self.store.add_feed("Test", "http://example.com/feed.rss",
                            "http://example.com/")
        self.assertEqual(self.store.list_entries(1, 10), [])

    def test_is_feed_id_false(self):
        self.assertFalse(self.store.is_feed_id(1))

    def test_is_feed_id_true(self):
        self.store.add_feed("Test", "http://example.com/feed.rss",
                            "http://example.com/")
        self.assertTrue(self.store.is_feed_id(1))
