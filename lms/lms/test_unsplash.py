# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import frappe
from frappe.tests import UnitTestCase

from lms.unsplash import get_by_keyword, get_random


class TestUnsplash(UnitTestCase):
    def setUp(self):
        # The test site has no 'unsplash_access_key' configured, so every
        # make_unsplash_request() call returns None without hitting the network.
        self.assertFalse(frappe.db.get_single_value("LMS Settings", "unsplash_access_key"))

    def test_get_random_without_params_returns_none(self):
        # Regression: get_random() with no params must not crash on params.items().
        self.assertIsNone(get_random())

    def test_get_by_keyword_returns_none_when_request_empty(self):
        # Regression: get_by_keyword() must not crash on data.get() when data is None.
        self.assertIsNone(get_by_keyword("cats"))
