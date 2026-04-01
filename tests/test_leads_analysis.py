"""
Tests para analysis/leads_analysis.py — Análisis de leads (DB + funciones puras).
"""

import unittest
from unittest.mock import patch
from tests.conftest import create_test_db, seed_clients, seed_leads
from analysis.leads_analysis import get_funnel_stats, group_leads_by_source


# ── Tests con BD ──────────────────────────────────────────────

class TestGetLeads(unittest.TestCase):
    """Tests para get_leads() con BD in-memory."""

    def setUp(self):
        self.conn = create_test_db()
        seed_clients(self.conn)
        seed_leads(self.conn)

    def tearDown(self):
        self.conn.real_close()

    @patch("analysis.leads_analysis.get_db_connection")
    def test_returns_all_leads(self, mock_conn):
        mock_conn.return_value = self.conn
        from analysis.leads_analysis import get_leads
        result = get_leads()
        self.assertEqual(len(result), 5)

    @patch("analysis.leads_analysis.get_db_connection")
    def test_filter_by_source(self, mock_conn):
        mock_conn.return_value = self.conn
        from analysis.leads_analysis import get_leads
        result = get_leads(source="meta_ads")
        self.assertEqual(len(result), 2)

    @patch("analysis.leads_analysis.get_db_connection")
    def test_filter_by_date_range(self, mock_conn):
        mock_conn.return_value = self.conn
        from analysis.leads_analysis import get_leads
        result = get_leads(start_date="2024-05-01", end_date="2024-05-05")
        self.assertGreaterEqual(len(result), 2)

    @patch("analysis.leads_analysis.get_db_connection")
    def test_enriched_with_client_name(self, mock_conn):
        mock_conn.return_value = self.conn
        from analysis.leads_analysis import get_leads
        result = get_leads()
        converted = [ld for ld in result if ld.get("client_id") == "C001"]
        if converted:
            self.assertEqual(converted[0]["client_name"], "TechNova")


class TestGetLeadsStats(unittest.TestCase):
    """Tests para get_leads_stats()."""

    def setUp(self):
        self.conn = create_test_db()
        seed_clients(self.conn)
        seed_leads(self.conn)

    def tearDown(self):
        self.conn.real_close()

    @patch("analysis.leads_analysis.get_db_connection")
    def test_counts_correct(self, mock_conn):
        mock_conn.return_value = self.conn
        from analysis.leads_analysis import get_leads_stats
        result = get_leads_stats()
        self.assertEqual(result["total_leads"], 5)
        self.assertEqual(result["with_meeting"], 2)  # meeting + converted
        self.assertEqual(result["with_client"], 1)    # solo L004

    @patch("analysis.leads_analysis.get_db_connection")
    def test_by_source_grouped(self, mock_conn):
        mock_conn.return_value = self.conn
        from analysis.leads_analysis import get_leads_stats
        result = get_leads_stats()
        self.assertIn("meta_ads", result["by_source"])
        self.assertEqual(result["by_source"]["meta_ads"], 2)

    @patch("analysis.leads_analysis.get_db_connection")
    def test_empty_table(self, mock_conn):
        conn = create_test_db()
        mock_conn.return_value = conn
        from analysis.leads_analysis import get_leads_stats
        result = get_leads_stats()
        self.assertEqual(result["total_leads"], 0)


class TestGetUniqueSources(unittest.TestCase):
    """Tests para get_unique_sources()."""

    def setUp(self):
        self.conn = create_test_db()
        seed_clients(self.conn)
        seed_leads(self.conn)

    def tearDown(self):
        self.conn.real_close()

    @patch("analysis.leads_analysis.get_db_connection")
    def test_returns_unique_sources(self, mock_conn):
        mock_conn.return_value = self.conn
        from analysis.leads_analysis import get_unique_sources
        result = get_unique_sources()
        self.assertIn("meta_ads", result)
        self.assertIn("google_ads", result)


# ── Tests funciones puras ─────────────────────────────────────

SAMPLE_LEADS = [
    {"id": "L1", "status": "new", "created_at": "2024-05-01", "meeting_date": None, "client_id": None},
    {"id": "L2", "status": "contacted", "created_at": "2024-05-02", "meeting_date": None, "client_id": None},
    {"id": "L3", "status": "meeting", "created_at": "2024-05-03", "meeting_date": "2024-05-10", "client_id": None},
    {"id": "L4", "status": "converted", "created_at": "2024-04-20", "meeting_date": "2024-04-25", "client_id": "C001"},
    {"id": "L5", "status": "lost", "created_at": "2024-05-08", "meeting_date": None, "client_id": None},
]


class TestGetFunnelStats(unittest.TestCase):
    """Tests para get_funnel_stats() — función pura."""

    def test_empty_list_returns_zeros(self):
        result = get_funnel_stats([])
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["meetings"], 0)
        self.assertEqual(result["converted"], 0)

    def test_all_statuses_counted(self):
        result = get_funnel_stats(SAMPLE_LEADS)
        self.assertEqual(result["total"], 5)
        self.assertEqual(result["meetings"], 2)    # meeting + converted
        self.assertEqual(result["converted"], 1)
        self.assertEqual(result["lost"], 1)

    def test_lead_to_meeting_percentage(self):
        result = get_funnel_stats(SAMPLE_LEADS)
        expected = 2 / 5 * 100
        self.assertAlmostEqual(result["lead_to_meeting_pct"], expected)

    def test_meeting_to_client_percentage(self):
        result = get_funnel_stats(SAMPLE_LEADS)
        # converted_from_meeting=1, meetings=2 → 50%
        self.assertAlmostEqual(result["meeting_to_client_pct"], 50.0)

    def test_avg_time_to_meeting(self):
        result = get_funnel_stats(SAMPLE_LEADS)
        # L3: 2024-05-10 - 2024-05-03 = 7 días
        # L4: 2024-04-25 - 2024-04-20 = 5 días
        # avg = 6.0
        self.assertAlmostEqual(result["avg_time_to_meeting"], 6.0)

    def test_zero_meetings_no_division_error(self):
        leads = [{"status": "new", "created_at": "2024-05-01"}]
        result = get_funnel_stats(leads)
        self.assertEqual(result["meeting_to_client_pct"], 0.0)

    def test_dropoff_calculated(self):
        result = get_funnel_stats(SAMPLE_LEADS)
        self.assertEqual(result["lead_dropoff"], 3)     # total - meetings
        self.assertEqual(result["meeting_dropoff"], 1)   # meetings - converted


class TestGroupLeadsBySource(unittest.TestCase):
    """Tests para group_leads_by_source() — función pura."""

    LEADS_BY_SOURCE = [
        {"source": "meta_ads", "status": "new", "created_at": "2024-05-01", "meeting_date": None, "client_id": None},
        {"source": "meta_ads", "status": "meeting", "created_at": "2024-05-02", "meeting_date": "2024-05-09", "client_id": None},
        {"source": "google_ads", "status": "converted", "created_at": "2024-04-20", "meeting_date": "2024-04-25", "client_id": "C001"},
        {"source": None, "status": "lost", "created_at": "2024-05-05", "meeting_date": None, "client_id": None},
    ]

    def test_groups_by_source(self):
        result = group_leads_by_source(self.LEADS_BY_SOURCE)
        self.assertIn("meta_ads", result)
        self.assertIn("google_ads", result)
        self.assertEqual(result["meta_ads"]["total"], 2)

    def test_meeting_to_client_pct_per_source(self):
        result = group_leads_by_source(self.LEADS_BY_SOURCE)
        # google_ads: 1 meeting (converted), 1 client_from_meeting → 100%
        self.assertAlmostEqual(result["google_ads"]["meeting_to_client_pct"], 100.0)

    def test_unknown_source_for_missing(self):
        result = group_leads_by_source(self.LEADS_BY_SOURCE)
        self.assertIn("unknown", result)
        self.assertEqual(result["unknown"]["total"], 1)

    def test_avg_time_to_meeting_per_source(self):
        result = group_leads_by_source(self.LEADS_BY_SOURCE)
        # meta_ads: L2 → 2024-05-09 - 2024-05-02 = 7 días
        self.assertAlmostEqual(result["meta_ads"]["avg_time_to_meeting"], 7.0)


if __name__ == "__main__":
    unittest.main()
