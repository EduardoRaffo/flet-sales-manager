"""
Tests para analysis/marketing_analysis.py — Métricas de marketing (DB + puras).
"""

import unittest
from unittest.mock import patch
from tests.conftest import create_test_db, seed_clients, seed_sales, seed_leads, seed_marketing_spend
from analysis.marketing_analysis import (
    compute_marketing_metrics_from_leads,
    compute_marketing_summary_from_metrics,
)


# ── Tests con BD ──────────────────────────────────────────────

class TestGetLeadsBySource(unittest.TestCase):
    """Tests para get_leads_by_source()."""

    def setUp(self):
        self.conn = create_test_db()
        seed_clients(self.conn)
        seed_leads(self.conn)

    def tearDown(self):
        self.conn.real_close()

    @patch("analysis.marketing_analysis.get_db_connection")
    def test_returns_grouped_counts(self, mock_conn):
        mock_conn.return_value = self.conn
        from analysis.marketing_analysis import get_leads_by_source
        result = get_leads_by_source()
        self.assertIsInstance(result, list)
        sources = {r["source"] for r in result}
        self.assertIn("meta_ads", sources)

    @patch("analysis.marketing_analysis.get_db_connection")
    def test_empty_returns_empty(self, mock_conn):
        conn = create_test_db()
        mock_conn.return_value = conn
        from analysis.marketing_analysis import get_leads_by_source
        result = get_leads_by_source()
        self.assertEqual(result, [])


class TestGetMarketingSpendBySource(unittest.TestCase):
    """Tests para get_marketing_spend_by_source()."""

    def setUp(self):
        self.conn = create_test_db()
        seed_marketing_spend(self.conn)

    def tearDown(self):
        self.conn.real_close()

    @patch("analysis.marketing_analysis.get_db_connection")
    def test_returns_grouped_spend(self, mock_conn):
        mock_conn.return_value = self.conn
        from analysis.marketing_analysis import get_marketing_spend_by_source
        result = get_marketing_spend_by_source()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        sources = {r["source"] for r in result}
        self.assertIn("meta_ads", sources)


class TestGetRevenuePerClient(unittest.TestCase):
    """Tests para get_revenue_per_client()."""

    def setUp(self):
        self.conn = create_test_db()
        seed_clients(self.conn)
        seed_sales(self.conn)

    def tearDown(self):
        self.conn.real_close()

    @patch("analysis.marketing_analysis.get_db_connection")
    def test_returns_revenue_dict(self, mock_conn):
        mock_conn.return_value = self.conn
        from analysis.marketing_analysis import get_revenue_per_client
        result = get_revenue_per_client()
        self.assertIsInstance(result, dict)
        self.assertIn("C001", result)
        self.assertEqual(result["C001"], 3000.0)  # 1000 + 2000


# ── Tests funciones puras ─────────────────────────────────────

class TestComputeMarketingMetricsFromLeads(unittest.TestCase):
    """Tests para compute_marketing_metrics_from_leads() — función pura."""

    LEADS = [
        {"source": "meta_ads", "status": "new", "created_at": "2024-05-01", "client_id": None},
        {"source": "meta_ads", "status": "converted", "created_at": "2024-05-02", "client_id": "C001"},
        {"source": "google_ads", "status": "new", "created_at": "2024-05-03", "client_id": None},
    ]
    SPEND = {"meta_ads": 500.0, "google_ads": 300.0}
    REVENUE = {"C001": 5000.0}

    def test_groups_by_source(self):
        result = compute_marketing_metrics_from_leads(self.LEADS, self.SPEND, self.REVENUE)
        sources = {r["source"] for r in result}
        self.assertIn("meta_ads", sources)
        self.assertIn("google_ads", sources)

    def test_calculates_cpl_cac_roi(self):
        result = compute_marketing_metrics_from_leads(self.LEADS, self.SPEND, self.REVENUE)
        meta = next(r for r in result if r["source"] == "meta_ads")
        self.assertEqual(meta["leads"], 2)
        self.assertEqual(meta["customers"], 1)
        self.assertEqual(meta["revenue"], 5000.0)
        self.assertEqual(meta["spend"], 500.0)
        self.assertEqual(meta["cpl"], 250.0)    # 500/2
        self.assertEqual(meta["cac"], 500.0)    # 500/1
        self.assertEqual(meta["roi"], 9.0)      # (5000-500)/500

    def test_empty_leads_empty_result(self):
        result = compute_marketing_metrics_from_leads([], {}, {})
        self.assertEqual(result, [])

    def test_spend_source_without_leads(self):
        result = compute_marketing_metrics_from_leads(
            [], {"orphan_source": 100.0}, {},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["source"], "orphan_source")
        self.assertEqual(result[0]["leads"], 0)

    def test_sorted_by_revenue_desc(self):
        result = compute_marketing_metrics_from_leads(self.LEADS, self.SPEND, self.REVENUE)
        revenues = [r["revenue"] for r in result]
        self.assertEqual(revenues, sorted(revenues, reverse=True))


class TestComputeMarketingSummaryFromMetrics(unittest.TestCase):
    """Tests para compute_marketing_summary_from_metrics() — función pura."""

    METRICS = [
        {"source": "meta_ads", "leads": 10, "customers": 2, "revenue": 5000.0, "spend": 500.0,
         "cpl": 50.0, "cac": 250.0, "roi": 9.0},
        {"source": "google_ads", "leads": 5, "customers": 1, "revenue": 2000.0, "spend": 300.0,
         "cpl": 60.0, "cac": 300.0, "roi": 5.67},
    ]

    def test_aggregates_totals(self):
        result = compute_marketing_summary_from_metrics(self.METRICS)
        self.assertEqual(result["total_leads"], 15)
        self.assertEqual(result["total_customers"], 3)
        self.assertEqual(result["total_revenue"], 7000.0)
        self.assertEqual(result["total_spend"], 800.0)

    def test_calculates_averages(self):
        result = compute_marketing_summary_from_metrics(self.METRICS)
        # avg_cpl = 800/15
        self.assertAlmostEqual(result["avg_cpl"], round(800 / 15, 2))
        # avg_cac = 800/3
        self.assertAlmostEqual(result["avg_cac"], round(800 / 3, 2))

    def test_zero_leads_safe_division(self):
        result = compute_marketing_summary_from_metrics([])
        self.assertEqual(result["total_leads"], 0)
        self.assertEqual(result["avg_cpl"], 0.0)
        self.assertEqual(result["conversion_rate"], 0.0)

    def test_conversion_rate(self):
        result = compute_marketing_summary_from_metrics(self.METRICS)
        expected = round(3 / 15, 4)
        self.assertAlmostEqual(result["conversion_rate"], expected)


if __name__ == "__main__":
    unittest.main()
