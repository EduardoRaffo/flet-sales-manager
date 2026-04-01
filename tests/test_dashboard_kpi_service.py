"""
Tests para services/dashboard_kpi_service.py — KPIs del Dashboard.
"""

import unittest
from unittest.mock import patch
from tests.conftest import create_test_db, seed_clients, seed_sales, seed_leads
from services.dashboard_kpi_service import DashboardKPIService


class TestBuildSnapshot(unittest.TestCase):
    """Tests para DashboardKPIService.build_snapshot()."""

    @patch("services.dashboard_kpi_service.get_connection")
    def test_empty_db_returns_no_data(self, mock_conn):
        conn = create_test_db()
        mock_conn.return_value = conn
        snap = DashboardKPIService.build_snapshot()
        self.assertFalse(snap.has_data)
        self.assertEqual(snap.sales_rows, 0)
        self.assertEqual(snap.clients_rows, 0)

    @patch("services.dashboard_kpi_service.get_connection")
    def test_with_sales_returns_correct_counts(self, mock_conn):
        conn = create_test_db()
        seed_clients(conn)
        seed_sales(conn)
        mock_conn.return_value = conn
        snap = DashboardKPIService.build_snapshot()
        self.assertTrue(snap.has_data)
        self.assertEqual(snap.sales_rows, 5)
        self.assertEqual(snap.clients_rows, 3)

    @patch("services.dashboard_kpi_service.get_connection")
    def test_with_leads_returns_stats(self, mock_conn):
        conn = create_test_db()
        seed_clients(conn)
        seed_leads(conn)
        mock_conn.return_value = conn
        snap = DashboardKPIService.build_snapshot()
        self.assertEqual(snap.total_leads, 5)
        self.assertEqual(snap.leads_with_meeting, 2)  # meeting + converted

    @patch("services.dashboard_kpi_service.get_connection")
    def test_conversion_rate_calculation(self, mock_conn):
        conn = create_test_db()
        seed_clients(conn)
        seed_leads(conn)
        mock_conn.return_value = conn
        snap = DashboardKPIService.build_snapshot()
        # 1 lead con client_id de 5 totales = 20.0%
        self.assertAlmostEqual(snap.leads_conversion_rate, 20.0)

    @patch("services.dashboard_kpi_service.get_connection")
    def test_zero_leads_conversion_zero(self, mock_conn):
        conn = create_test_db()
        seed_clients(conn)
        seed_sales(conn)
        mock_conn.return_value = conn
        snap = DashboardKPIService.build_snapshot()
        self.assertEqual(snap.leads_conversion_rate, 0.0)

    @patch("services.dashboard_kpi_service.get_connection")
    def test_last_import_from_metadata(self, mock_conn):
        conn = create_test_db()
        conn.execute(
            "INSERT INTO import_metadata (imported_at, file_name) VALUES (?, ?)",
            ("2024-05-15T10:30:00", "test.csv"),
        )
        conn.commit()
        mock_conn.return_value = conn
        snap = DashboardKPIService.build_snapshot()
        self.assertEqual(snap.last_import, "2024-05-15T10:30:00")


class TestFormatLastImport(unittest.TestCase):
    """Tests para _format_last_import()."""

    def test_none_returns_dash(self):
        result = DashboardKPIService._format_last_import(None)
        self.assertEqual(result, "—")

    def test_valid_iso_formatted(self):
        result = DashboardKPIService._format_last_import("2024-05-15T10:30:00")
        self.assertEqual(result, "15/05/2024 10:30")

    def test_invalid_returns_raw(self):
        result = DashboardKPIService._format_last_import("bad-date")
        self.assertEqual(result, "bad-date")

    def test_empty_string_returns_dash(self):
        result = DashboardKPIService._format_last_import("")
        self.assertEqual(result, "—")


if __name__ == "__main__":
    unittest.main()
