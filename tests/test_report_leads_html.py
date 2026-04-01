"""
Tests para reports/report_leads_html.py — Informe HTML de leads.
"""

import os
import tempfile
import unittest
from unittest.mock import patch
from reports.report_leads_html import generate_leads_html_report


class TestGenerateLeadsHtmlReport(unittest.TestCase):
    """Tests para generate_leads_html_report()."""

    LEADS = [
        {"id": "L1", "source": "meta_ads", "status": "new", "created_at": "2024-05-01",
         "meeting_date": None, "client_id": None, "client_name": None},
        {"id": "L2", "source": "google_ads", "status": "converted", "created_at": "2024-05-02",
         "meeting_date": "2024-05-10", "client_id": "C001", "client_name": "TechNova"},
    ]

    FUNNEL = {
        "total": 2, "meetings": 1, "converted": 1, "lost": 0,
        "lead_to_meeting_pct": 50.0, "meeting_to_client_pct": 100.0,
        "avg_time_to_meeting": 8.0,
        "lead_dropoff": 1, "meeting_dropoff": 0,
    }

    SOURCES = {
        "meta_ads": {"total": 1, "meetings": 0, "clients": 0, "meeting_to_client_pct": 0, "avg_time_to_meeting": 0},
        "google_ads": {"total": 1, "meetings": 1, "clients": 1, "meeting_to_client_pct": 100, "avg_time_to_meeting": 8},
    }

    @patch("reports.report_leads_html.generate_pie_chart", return_value="fakeb64")
    def test_generates_file(self, mock_pie):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test_leads.html")
            ok, msg, filepath = generate_leads_html_report(
                self.LEADS, self.FUNNEL, self.SOURCES, filename=path,
            )
            self.assertTrue(ok)
            self.assertTrue(os.path.exists(filepath))

    @patch("reports.report_leads_html.generate_pie_chart", return_value="fakeb64")
    def test_contains_funnel(self, mock_pie):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test_leads.html")
            ok, msg, filepath = generate_leads_html_report(
                self.LEADS, self.FUNNEL, self.SOURCES, filename=path,
            )
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("Embudo", content)
            self.assertIn("Leads", content)

    @patch("reports.report_leads_html.generate_pie_chart", return_value="fakeb64")
    def test_source_labels(self, mock_pie):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test_leads.html")
            ok, msg, filepath = generate_leads_html_report(
                self.LEADS, self.FUNNEL, self.SOURCES, filename=path,
            )
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("Meta Ads", content)
            self.assertIn("Google Ads", content)


if __name__ == "__main__":
    unittest.main()
