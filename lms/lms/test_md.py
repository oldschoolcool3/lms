# Copyright (c) 2021, FOSS United and Contributors
# See license.txt

from frappe.tests import UnitTestCase

from lms.lms.md import sanitize_html


class TestMd(UnitTestCase):
    def test_sanitize_html_handles_bodyless_input(self):
        """sanitize_html must not raise when BeautifulSoup yields no body (empty/malformed html)."""
        for html in ("", "   ", "<>", "not html"):
            result = sanitize_html(html, "YouTubeVideo")
            self.assertIsInstance(result, str)
