"""
Tests para analysis/date_analysis.py — Rango de fechas disponibles.
"""

import unittest
from unittest.mock import patch
from tests.conftest import create_test_db, seed_clients, seed_sales


class TestGetDateRange(unittest.TestCase):
    """Tests para get_date_range()."""

    def setUp(self):
        self.conn = create_test_db()
        seed_clients(self.conn)

    def tearDown(self):
        self.conn.real_close()

    @patch("analysis.date_analysis.get_db_connection")
    def test_returns_min_max_dates(self, mock_conn):
        seed_sales(self.conn)
        mock_conn.return_value = self.conn
        from analysis.date_analysis import get_date_range
        min_d, max_d = get_date_range()
        self.assertEqual(min_d, "2024-04-15")
        self.assertEqual(max_d, "2024-05-12")

    @patch("analysis.date_analysis.get_db_connection")
    def test_empty_table_returns_none(self, mock_conn):
        mock_conn.return_value = self.conn
        from analysis.date_analysis import get_date_range
        min_d, max_d = get_date_range()
        self.assertIsNone(min_d)
        self.assertIsNone(max_d)

    @patch("analysis.date_analysis.get_db_connection")
    def test_single_date(self, mock_conn):
        seed_sales(self.conn, [("TechNova", "C001", "Servicio", 1000.0, "2024-05-15")])
        mock_conn.return_value = self.conn
        from analysis.date_analysis import get_date_range
        min_d, max_d = get_date_range()
        self.assertEqual(min_d, "2024-05-15")
        self.assertEqual(max_d, "2024-05-15")


if __name__ == "__main__":
    unittest.main()
