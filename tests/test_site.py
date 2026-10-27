"""Dependency-free checks for the CityBike lab website."""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "index.html"


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.h1_count = 0
        self.html_lang = False

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if "id" in d:
            self.ids.append(d["id"])
        if tag == "h1":
            self.h1_count += 1
        if tag == "html" and d.get("lang") == "en":
            self.html_lang = True


class SiteQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")
        cls.parsed = Tags()
        cls.parsed.feed(cls.html)

    def test_has_accessible_page_structure(self):
        self.assertTrue(self.parsed.html_lang, "HTML document should declare lang=en")
        self.assertEqual(self.parsed.h1_count, 1, "Page should have exactly one h1")

    def test_required_dashboard_sections_exist(self):
        self.assertIn("service-list", self.parsed.ids)
        self.assertIn("updates", self.parsed.ids)
        self.assertIn("latest-update", self.parsed.ids)

    def test_css_file_exists(self):
        self.assertTrue((ROOT / "assets" / "styles.css").is_file())
        self.assertIn('href="assets/styles.css"', self.html)

    def test_merge_conflict_markers_are_absent(self):
        self.assertNotRegex(self.html, r"(?m)^(?:<<<<<<< |=======\s*$|>>>>>>> )")

    def test_no_demo_credentials_in_repository(self):
        for path in (PAGE, ROOT / "README.md"):
            contents = path.read_text(encoding="utf-8")
            self.assertNotRegex(contents, r"(?i)(password|api[_-]?key)\s*[:=]\s*['\"]?\S{6,}")


if __name__ == "__main__":
    unittest.main()
