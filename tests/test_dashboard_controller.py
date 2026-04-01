"""
Tests para controllers/dashboard_controller.py — Dashboard controller.
"""

import unittest
from unittest.mock import patch
from controllers.dashboard_controller import DashboardController
from domain.dashboard_kpi_snapshot import DashboardKPISnapshot


class TestClearTables(unittest.TestCase):
    """Tests para clear_sales/clients/leads."""

    @patch("controllers.dashboard_controller.clear_sales_table", return_value=True)
    def test_clear_sales_success(self, mock_clear):
        ok, msg = DashboardController.clear_sales()
        self.assertTrue(ok)
        mock_clear.assert_called_once()

    @patch("controllers.dashboard_controller.clear_sales_table", return_value=False)
    def test_clear_sales_failure(self, mock_clear):
        ok, msg = DashboardController.clear_sales()
        self.assertFalse(ok)
        self.assertIn("Error", msg)

    @patch("controllers.dashboard_controller.clear_clients_table", return_value=True)
    def test_clear_clients_success(self, mock_clear):
        ok, msg = DashboardController.clear_clients()
        self.assertTrue(ok)

    @patch("controllers.dashboard_controller.clear_clients_table", return_value=False)
    def test_clear_clients_failure(self, mock_clear):
        ok, msg = DashboardController.clear_clients()
        self.assertFalse(ok)

    @patch("controllers.dashboard_controller.clear_leads_table", return_value=True)
    def test_clear_leads_success(self, mock_clear):
        ok, msg = DashboardController.clear_leads()
        self.assertTrue(ok)

    @patch("controllers.dashboard_controller.clear_leads_table", return_value=False)
    def test_clear_leads_failure(self, mock_clear):
        ok, msg = DashboardController.clear_leads()
        self.assertFalse(ok)


class TestGetDashboardKPISnapshot(unittest.TestCase):
    """Tests para get_dashboard_kpi_snapshot()."""

    @patch("controllers.dashboard_controller.DashboardKPIService.build_snapshot")
    def test_returns_snapshot(self, mock_build):
        snap = DashboardKPISnapshot.empty()
        mock_build.return_value = snap
        result = DashboardController.get_dashboard_kpi_snapshot()
        self.assertIsInstance(result, DashboardKPISnapshot)

    @patch("controllers.dashboard_controller.DashboardKPIService.build_snapshot", side_effect=Exception("DB error"))
    def test_exception_returns_empty(self, mock_build):
        result = DashboardController.get_dashboard_kpi_snapshot()
        self.assertIsInstance(result, DashboardKPISnapshot)
        self.assertFalse(result.has_data)


if __name__ == "__main__":
    unittest.main()
