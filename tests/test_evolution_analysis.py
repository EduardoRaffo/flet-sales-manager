"""
Tests para analysis/evolution_analysis.py — Evolución temporal de ventas.
"""

import unittest
from unittest.mock import patch
from tests.conftest import create_test_db, seed_clients, seed_sales


class TestGetSalesEvolution(unittest.TestCase):
    """Tests para get_sales_evolution()."""

    def setUp(self):
        self.conn = create_test_db()
        seed_clients(self.conn)
        seed_sales(self.conn)

    def tearDown(self):
        self.conn.real_close()

    @patch("analysis.evolution_analysis.get_db_connection")
    def test_daily_grouping(self, mock_conn):
        mock_conn.return_value = self.conn
        from analysis.evolution_analysis import get_sales_evolution
        df = get_sales_evolution(grouping="day")
        self.assertIsNotNone(df)
        self.assertGreater(len(df), 0)

    @patch("analysis.evolution_analysis.get_db_connection")
    def test_monthly_grouping(self, mock_conn):
        # Seed 3+ months of data to avoid Polars 2-row column-orientation ambiguity
        conn = create_test_db()
        seed_clients(conn)
        seed_sales(conn, rows=[
            ("TechNova", "C001", "Servicio", 1000.0, "2024-03-15"),
            ("TechNova", "C001", "Servicio", 500.0, "2024-04-10"),
            ("DataCorp", "C002", "Producto", 2000.0, "2024-05-01"),
            ("CloudSoft", "C003", "Servicio", 800.0, "2024-06-20"),
        ])
        mock_conn.return_value = conn
        from analysis.evolution_analysis import get_sales_evolution
        df = get_sales_evolution(grouping="month")
        self.assertIsNotNone(df)
        dates = df["date"].to_list()
        for d in dates:
            self.assertRegex(d, r"^\d{4}-\d{2}$")

    @patch("analysis.evolution_analysis.get_db_connection")
    def test_quarterly_grouping(self, mock_conn):
        mock_conn.return_value = self.conn
        from analysis.evolution_analysis import get_sales_evolution
        df = get_sales_evolution(grouping="quarter")
        self.assertIsNotNone(df)

    @patch("analysis.evolution_analysis.get_db_connection")
    def test_yearly_grouping(self, mock_conn):
        mock_conn.return_value = self.conn
        from analysis.evolution_analysis import get_sales_evolution
        df = get_sales_evolution(grouping="year")
        self.assertIsNotNone(df)

    @patch("analysis.evolution_analysis.get_db_connection")
    def test_empty_returns_none(self, mock_conn):
        conn = create_test_db()
        mock_conn.return_value = conn
        from analysis.evolution_analysis import get_sales_evolution
        df = get_sales_evolution(grouping="day")
        self.assertIsNone(df)

    @patch("analysis.evolution_analysis.get_db_connection")
    def test_with_filters(self, mock_conn):
        # Seed extra TechNova sales across 3+ days to avoid Polars ambiguity
        conn = create_test_db()
        seed_clients(conn)
        seed_sales(conn, rows=[
            ("TechNova", "C001", "Servicio", 1000.0, "2024-05-01"),
            ("TechNova", "C001", "Producto", 2000.0, "2024-05-05"),
            ("TechNova", "C001", "Servicio", 500.0, "2024-05-10"),
        ])
        mock_conn.return_value = conn
        from analysis.evolution_analysis import get_sales_evolution
        df = get_sales_evolution(
            start_date="2024-05-01", end_date="2024-05-31",
            client_name="TechNova", grouping="day",
        )
        self.assertIsNotNone(df)

    @patch("analysis.evolution_analysis.get_db_connection")
    def test_week_grouping_uses_iso_boundary(self, mock_conn):
        from analysis.evolution_analysis import get_sales_evolution

        boundary_conn = create_test_db()
        seed_clients(boundary_conn)
        # 3+ weeks of data to avoid Polars 2-row ambiguity
        seed_sales(
            boundary_conn,
            rows=[
                ("TechNova", "C001", "Servicio", 100.0, "2024-12-16"),
                ("TechNova", "C001", "Servicio", 100.0, "2024-12-23"),
                ("TechNova", "C001", "Servicio", 100.0, "2024-12-30"),
                ("TechNova", "C001", "Servicio", 200.0, "2025-01-01"),
            ],
        )
        mock_conn.return_value = boundary_conn

        df = get_sales_evolution(grouping="week")
        self.assertIsNotNone(df)
        self.assertGreater(len(df), 0)


class TestGetCompareEvolutionRows(unittest.TestCase):
    """Tests para get_compare_evolution_rows()."""

    def setUp(self):
        self.conn = create_test_db()
        seed_clients(self.conn)
        seed_sales(self.conn)

    def tearDown(self):
        self.conn.real_close()

    @patch("analysis.evolution_analysis.get_db_connection")
    def test_returns_aligned_rows(self, mock_conn):
        mock_conn.return_value = self.conn
        from analysis.evolution_analysis import get_compare_evolution_rows
        result = get_compare_evolution_rows(
            "2024-04-01", "2024-04-30",
            "2024-05-01", "2024-05-31",
            grouping="month",
        )
        self.assertIn("rows", result)
        self.assertIn("meta", result)
        self.assertEqual(result["meta"]["grouping"], "month")

    @patch("analysis.evolution_analysis.get_db_connection")
    def test_result_structure(self, mock_conn):
        mock_conn.return_value = self.conn
        from analysis.evolution_analysis import get_compare_evolution_rows
        result = get_compare_evolution_rows(
            "2024-05-01", "2024-05-15",
            "2024-05-16", "2024-05-31",
            grouping="day",
        )
        for row in result["rows"]:
            self.assertIn("label", row)
            self.assertIn("A", row)
            self.assertIn("B", row)


if __name__ == "__main__":
    unittest.main()
