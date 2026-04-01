"""
Tests para analysis/sales_analysis.py — Análisis de ventas y productos.
"""

import unittest
from unittest.mock import patch, MagicMock
from tests.conftest import create_test_db, seed_clients, seed_sales


class TestGetUniqueProducts(unittest.TestCase):
    """Tests para get_unique_products()."""

    def setUp(self):
        self.conn = create_test_db()
        seed_clients(self.conn)

    def tearDown(self):
        self.conn.real_close()

    @patch("analysis.sales_analysis.get_db_connection")
    def test_returns_distinct_products(self, mock_conn):
        seed_sales(self.conn)
        mock_conn.return_value = self.conn
        from analysis.sales_analysis import get_unique_products
        result = get_unique_products()
        self.assertIsInstance(result, list)
        self.assertIn("Servicio", result)
        self.assertIn("Producto", result)
        self.assertEqual(len(result), 2)

    @patch("analysis.sales_analysis.get_db_connection")
    def test_empty_table_returns_empty_list(self, mock_conn):
        mock_conn.return_value = self.conn
        from analysis.sales_analysis import get_unique_products
        result = get_unique_products()
        self.assertEqual(result, [])

    @patch("analysis.sales_analysis.get_db_connection")
    def test_products_sorted_alphabetically(self, mock_conn):
        seed_sales(self.conn)
        mock_conn.return_value = self.conn
        from analysis.sales_analysis import get_unique_products
        result = get_unique_products()
        self.assertEqual(result, sorted(result))


class TestGetSalesSummary(unittest.TestCase):
    """Tests para get_sales_summary()."""

    def setUp(self):
        self.conn = create_test_db()
        seed_clients(self.conn)
        seed_sales(self.conn)

    def tearDown(self):
        self.conn.real_close()

    @patch("analysis.sales_analysis.get_db_connection")
    def test_returns_dataframe_and_average(self, mock_conn):
        mock_conn.return_value = self.conn
        from analysis.sales_analysis import get_sales_summary
        df, avg = get_sales_summary()
        self.assertIsNotNone(df)
        self.assertIsNotNone(avg)
        self.assertGreater(avg, 0)

    @patch("analysis.sales_analysis.get_db_connection")
    def test_filter_by_date_range(self, mock_conn):
        mock_conn.return_value = self.conn
        from analysis.sales_analysis import get_sales_summary
        df, avg = get_sales_summary(start_date="2024-05-01", end_date="2024-05-31")
        self.assertIsNotNone(df)

    @patch("analysis.sales_analysis.get_db_connection")
    def test_filter_by_client(self, mock_conn):
        mock_conn.return_value = self.conn
        from analysis.sales_analysis import get_sales_summary
        df, avg = get_sales_summary(client_name="TechNova")
        self.assertIsNotNone(df)

    @patch("analysis.sales_analysis.get_db_connection")
    def test_filter_by_product(self, mock_conn):
        mock_conn.return_value = self.conn
        from analysis.sales_analysis import get_sales_summary
        df, avg = get_sales_summary(product_type="Servicio")
        self.assertIsNotNone(df)

    @patch("analysis.sales_analysis.get_db_connection")
    def test_empty_result_returns_none_none(self, mock_conn):
        mock_conn.return_value = self.conn
        from analysis.sales_analysis import get_sales_summary
        df, avg = get_sales_summary(client_name="NonExistent")
        self.assertIsNone(df)
        self.assertIsNone(avg)


class TestGetSalesWithClientInfo(unittest.TestCase):
    """Tests para get_sales_with_client_info()."""

    def setUp(self):
        self.conn = create_test_db()
        seed_clients(self.conn)
        seed_sales(self.conn)

    def tearDown(self):
        self.conn.real_close()

    @patch("analysis.sales_analysis.get_client_by_id_cached")
    @patch("analysis.sales_analysis.get_db_connection")
    def test_returns_enriched_sales_list(self, mock_conn, mock_client):
        mock_conn.return_value = self.conn
        mock_client.return_value = ("C001", "TechNova", "A12345678", "Calle 1", "Juan", "juan@tech.com")
        from analysis.sales_analysis import get_sales_with_client_info
        result = get_sales_with_client_info()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn("client_cif", result[0])

    @patch("analysis.sales_analysis.get_client_by_id_cached")
    @patch("analysis.sales_analysis.get_db_connection")
    def test_missing_client_info_uses_defaults(self, mock_conn, mock_client):
        mock_conn.return_value = self.conn
        mock_client.return_value = None
        from analysis.sales_analysis import get_sales_with_client_info
        result = get_sales_with_client_info()
        self.assertGreater(len(result), 0)
        self.assertEqual(result[0]["client_cif"], "-")
        self.assertEqual(result[0]["client_email"], "-")


if __name__ == "__main__":
    unittest.main()
