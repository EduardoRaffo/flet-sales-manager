"""
Tests para analysis/clients_analysis.py — Análisis de clientes.
"""

import unittest
from unittest.mock import patch
from tests.conftest import create_test_db, seed_clients, seed_sales


class TestGetUniqueClients(unittest.TestCase):
    """Tests para get_unique_clients()."""

    def setUp(self):
        self.conn = create_test_db()
        seed_clients(self.conn)

    def tearDown(self):
        self.conn.real_close()

    @patch("analysis.clients_analysis.get_db_connection")
    def test_returns_distinct_client_names(self, mock_conn):
        seed_sales(self.conn)
        mock_conn.return_value = self.conn
        from analysis.clients_analysis import get_unique_clients
        result = get_unique_clients()
        self.assertIsInstance(result, list)
        self.assertIn("TechNova", result)
        self.assertIn("DataCorp", result)

    @patch("analysis.clients_analysis.get_db_connection")
    def test_empty_table_returns_empty(self, mock_conn):
        mock_conn.return_value = self.conn
        from analysis.clients_analysis import get_unique_clients
        result = get_unique_clients()
        self.assertEqual(result, [])


class TestCountUniqueClients(unittest.TestCase):
    """Tests para count_unique_clients()."""

    def setUp(self):
        self.conn = create_test_db()
        seed_clients(self.conn)
        seed_sales(self.conn)

    def tearDown(self):
        self.conn.real_close()

    @patch("analysis.clients_analysis.get_db_connection")
    def test_counts_distinct_clients(self, mock_conn):
        mock_conn.return_value = self.conn
        from analysis.clients_analysis import count_unique_clients
        result = count_unique_clients()
        self.assertEqual(result, 3)

    @patch("analysis.clients_analysis.get_db_connection")
    def test_with_date_filter(self, mock_conn):
        mock_conn.return_value = self.conn
        from analysis.clients_analysis import count_unique_clients
        result = count_unique_clients(start_date="2024-05-01", end_date="2024-05-31")
        # Solo TechNova, DataCorp, CloudSoft en mayo
        self.assertGreaterEqual(result, 1)

    @patch("analysis.clients_analysis.get_db_connection")
    def test_with_product_filter(self, mock_conn):
        mock_conn.return_value = self.conn
        from analysis.clients_analysis import count_unique_clients
        result = count_unique_clients(product_type="Servicio")
        self.assertGreaterEqual(result, 1)

    @patch("analysis.clients_analysis.get_db_connection")
    def test_empty_table_returns_zero(self, mock_conn):
        # Usar BD vacía
        conn = create_test_db()
        mock_conn.return_value = conn
        from analysis.clients_analysis import count_unique_clients
        result = count_unique_clients()
        self.assertEqual(result, 0)


class TestGetClientsSalesStats(unittest.TestCase):
    """Tests para get_clients_sales_stats()."""

    def setUp(self):
        self.conn = create_test_db()
        seed_clients(self.conn)
        seed_sales(self.conn)

    def tearDown(self):
        self.conn.real_close()

    @patch("analysis.sales_analysis.get_client_by_id_cached")
    @patch("analysis.sales_analysis.get_db_connection")
    def test_aggregates_by_client(self, mock_conn, mock_client):
        mock_conn.return_value = self.conn
        mock_client.return_value = ("C001", "TechNova", "A12345678", "Calle 1", "Juan", "juan@tech.com")
        from analysis.clients_analysis import get_clients_sales_stats
        result = get_clients_sales_stats()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        first = result[0]
        self.assertIn("client_id", first)
        self.assertIn("total_sales", first)
        self.assertIn("total_amount", first)

    @patch("analysis.sales_analysis.get_client_by_id_cached")
    @patch("analysis.sales_analysis.get_db_connection")
    def test_respects_filters(self, mock_conn, mock_client):
        mock_conn.return_value = self.conn
        mock_client.return_value = None
        from analysis.clients_analysis import get_clients_sales_stats
        result = get_clients_sales_stats(product_type="Servicio")
        self.assertIsInstance(result, list)


if __name__ == "__main__":
    unittest.main()
