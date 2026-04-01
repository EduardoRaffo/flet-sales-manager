"""
Tests para reports/html_template.py — Template HTML base.
"""

import unittest
from reports.html_template import get_html_base


class TestGetHtmlBase(unittest.TestCase):
    """Tests para get_html_base()."""

    def test_contains_content(self):
        result = get_html_base("<div>Test Content</div>", "Mi Titulo")
        self.assertIn("<div>Test Content</div>", result)

    def test_custom_title(self):
        result = get_html_base("<p>body</p>", "Informe Ventas 2024")
        self.assertIn("<title>Informe Ventas 2024</title>", result)

    def test_valid_html_structure(self):
        result = get_html_base("<p>test</p>")
        self.assertTrue(result.strip().startswith("<!DOCTYPE html>"))
        self.assertIn("<html", result)
        self.assertIn("<body", result)
        self.assertIn("</html>", result)

    def test_default_title(self):
        result = get_html_base("<p>test</p>")
        self.assertIn("<title>Informe - FDT</title>", result)


if __name__ == "__main__":
    unittest.main()
