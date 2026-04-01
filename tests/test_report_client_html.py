"""
Tests para reports/report_client_html.py — Informe HTML de cliente.
"""

import os
import tempfile
import unittest
from reports.report_client_html import generate_client_html_report


class TestGenerateClientHtmlReport(unittest.TestCase):
    """Tests para generate_client_html_report()."""

    CLIENT_INFO = {
        "client_id": "C001",
        "name": "TechNova",
        "cif": "B12345678",
        "address": "Calle Test 1",
        "contact_person": "Juan",
        "email": "info@technova.com",
    }

    STATS = {
        "total_sales": 5,
        "total_amount": 15000.0,
        "avg_amount": 3000.0,
        "sales": [
            {"date": "2024-05-01", "product_type": "Servicio", "price": 3000.0},
        ],
    }

    def test_generates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test_client.html")
            ok, msg, filepath = generate_client_html_report(self.CLIENT_INFO, self.STATS, filename=path)
            self.assertTrue(ok)
            self.assertTrue(os.path.exists(filepath))

    def test_contains_client_info(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test_client.html")
            ok, msg, filepath = generate_client_html_report(self.CLIENT_INFO, self.STATS, filename=path)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("TechNova", content)
            self.assertIn("B12345678", content)
            self.assertIn("info@technova.com", content)

    def test_escapes_html(self):
        """Verifica que caracteres especiales se escapan."""
        client = dict(self.CLIENT_INFO)
        client["name"] = "<script>alert('xss')</script>"
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test_escape.html")
            ok, msg, filepath = generate_client_html_report(client, self.STATS, filename=path)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertNotIn("<script>", content)
            self.assertIn("&lt;script&gt;", content)


if __name__ == "__main__":
    unittest.main()
