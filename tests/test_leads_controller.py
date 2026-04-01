"""
Tests para controllers/leads_controller.py — Controlador de leads.
"""

import unittest
from unittest.mock import patch, MagicMock
from controllers.leads_controller import LeadsController


class TestGetLeadsData(unittest.TestCase):
    """Tests para LeadsController.get_leads_data()."""

    @patch("controllers.leads_controller.get_leads", return_value=[{"id": "L1"}])
    def test_delegates_to_analysis(self, mock_get):
        result = LeadsController.get_leads_data(start_date="2024-05-01")
        self.assertEqual(len(result), 1)
        mock_get.assert_called_once_with(
            start_date="2024-05-01", end_date=None, source=None, status=None
        )

    @patch("controllers.leads_controller.get_leads", side_effect=Exception("DB error"))
    def test_error_returns_empty(self, mock_get):
        result = LeadsController.get_leads_data()
        self.assertEqual(result, [])


class TestGetLeadsStats(unittest.TestCase):
    """Tests para LeadsController.get_leads_stats()."""

    @patch("controllers.leads_controller.get_leads_stats", return_value={"total_leads": 5, "with_meeting": 2, "with_client": 1})
    def test_delegates(self, mock_stats):
        result = LeadsController.get_leads_stats()
        self.assertEqual(result["total_leads"], 5)

    @patch("controllers.leads_controller.get_leads_stats", side_effect=Exception("err"))
    def test_error_returns_defaults(self, mock_stats):
        result = LeadsController.get_leads_stats()
        self.assertEqual(result["total_leads"], 0)
        self.assertEqual(result["with_meeting"], 0)


class TestFunnelAndSourceDelegation(unittest.TestCase):
    """Tests para funnel_stats y group_by_source (wrappers puros)."""

    def test_funnel_stats_delegates(self):
        leads = [
            {"status": "new", "created_at": "2024-05-01"},
            {"status": "meeting", "created_at": "2024-05-02", "meeting_date": "2024-05-10"},
        ]
        result = LeadsController.get_funnel_stats(leads)
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["meetings"], 1)

    def test_group_by_source_delegates(self):
        leads = [
            {"source": "meta_ads", "status": "new", "created_at": "2024-05-01", "meeting_date": None, "client_id": None},
        ]
        result = LeadsController.group_leads_by_source(leads)
        self.assertIn("meta_ads", result)


class TestUpdateLeadInfo(unittest.TestCase):
    """Tests para LeadsController.update_lead_info()."""

    def test_empty_id_rejected(self):
        ok, msg = LeadsController.update_lead_info("", "new", None)
        self.assertFalse(ok)
        self.assertIn("ID", msg)

    @patch("controllers.leads_controller.validate_lead_status", return_value=False)
    def test_invalid_status_rejected(self, mock_validate):
        ok, msg = LeadsController.update_lead_info("L001", "bad_status", None)
        self.assertFalse(ok)
        self.assertIn("Estado", msg)

    @patch("controllers.leads_controller.validate_meeting_date", return_value=False)
    @patch("controllers.leads_controller.validate_lead_status", return_value=True)
    def test_invalid_meeting_date_rejected(self, mock_status, mock_date):
        ok, msg = LeadsController.update_lead_info("L001", "meeting", "not-a-date")
        self.assertFalse(ok)
        self.assertIn("fecha", msg.lower())

    @patch("controllers.leads_controller.update_lead_status_and_meeting")
    @patch("controllers.leads_controller.validate_meeting_date", return_value=True)
    @patch("controllers.leads_controller.validate_lead_status", return_value=True)
    def test_success(self, mock_status, mock_date, mock_update):
        ok, msg = LeadsController.update_lead_info("L001", "meeting", "2024-05-10")
        self.assertTrue(ok)
        mock_update.assert_called_once()

    @patch("controllers.leads_controller.update_lead_status_and_meeting")
    @patch("controllers.leads_controller.validate_meeting_date", return_value=True)
    @patch("controllers.leads_controller.validate_lead_status", return_value=True)
    def test_empty_meeting_date_normalised_to_none(self, mock_status, mock_date, mock_update):
        ok, msg = LeadsController.update_lead_info("L001", "new", "")
        self.assertTrue(ok)
        mock_update.assert_called_once_with("L001", "new", None)


if __name__ == "__main__":
    unittest.main()
