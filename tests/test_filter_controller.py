"""
Tests para controllers/filter_controller.py — Lógica pura de filtros.
"""

import unittest
from unittest.mock import MagicMock
from controllers.filter_controller import FilterController


class TestFilterControllerSetters(unittest.TestCase):
    """Tests para setters de filtros."""

    def test_set_start_date_returns_iso(self):
        fc = FilterController()
        result = fc.set_start_date("2024-05-15")
        self.assertEqual(result, "2024-05-15")
        self.assertEqual(fc.start_date, "2024-05-15")

    def test_set_end_date_returns_iso(self):
        fc = FilterController()
        result = fc.set_end_date("2024-05-31")
        self.assertEqual(result, "2024-05-31")

    def test_set_client_todos_becomes_none(self):
        fc = FilterController()
        result = fc.set_client("TODOS")
        self.assertIsNone(result)
        self.assertIsNone(fc.client_name)

    def test_set_client_strips_whitespace(self):
        fc = FilterController()
        result = fc.set_client("  TechNova  ")
        self.assertEqual(result, "TechNova")

    def test_set_product_todos_becomes_none(self):
        fc = FilterController()
        result = fc.set_product("TODOS")
        self.assertIsNone(result)

    def test_set_client_no_change_no_notify(self):
        fc = FilterController()
        fc.on_change = MagicMock()
        fc.set_client("TechNova")
        fc.on_change.reset_mock()
        fc.set_client("TechNova")
        fc.on_change.assert_not_called()

    def test_set_product_no_change_no_notify(self):
        fc = FilterController()
        fc.on_change = MagicMock()
        fc.set_product("Servicio")
        fc.on_change.reset_mock()
        fc.set_product("Servicio")
        fc.on_change.assert_not_called()


class TestFilterControllerRanges(unittest.TestCase):
    """Tests para rangos rápidos."""

    def test_apply_quick_range(self):
        fc = FilterController()
        start, end = fc.apply_quick_range(7)
        self.assertIsNotNone(start)
        self.assertIsNotNone(end)
        self.assertLessEqual(start, end)

    def test_apply_month_range(self):
        fc = FilterController()
        start, end = fc.apply_month_range()
        self.assertTrue(start.endswith("-01"))

    def test_apply_year_range(self):
        fc = FilterController()
        start, end = fc.apply_year_range()
        self.assertTrue(start.endswith("-01-01"))


class TestFilterControllerValidation(unittest.TestCase):
    """Tests para validación de filtros."""

    def test_both_none_is_valid(self):
        fc = FilterController()
        valid, msg = fc.validate()
        self.assertTrue(valid)
        self.assertIsNone(msg)

    def test_start_only_is_valid(self):
        fc = FilterController()
        fc.start_date = "2024-05-01"
        valid, msg = fc.validate()
        self.assertTrue(valid)

    def test_end_only_is_valid(self):
        fc = FilterController()
        fc.end_date = "2024-05-31"
        valid, msg = fc.validate()
        self.assertTrue(valid)

    def test_start_after_end_invalid(self):
        fc = FilterController()
        fc.start_date = "2024-06-01"
        fc.end_date = "2024-05-01"
        valid, msg = fc.validate()
        self.assertFalse(valid)
        self.assertIsNotNone(msg)


class TestFilterControllerState(unittest.TestCase):
    """Tests para estado de filtros."""

    def test_has_active_filter_false_initially(self):
        fc = FilterController()
        self.assertFalse(fc.has_active_filter())

    def test_has_active_filter_true_after_set(self):
        fc = FilterController()
        fc.set_start_date("2024-05-01")
        self.assertTrue(fc.has_active_filter())

    def test_clear_resets_all(self):
        fc = FilterController()
        fc.set_start_date("2024-05-01")
        fc.set_client("TechNova")
        fc.clear()
        self.assertFalse(fc.has_active_filter())
        self.assertIsNone(fc.start_date)
        self.assertIsNone(fc.client_name)

    def test_get_filter_params_returns_dict(self):
        fc = FilterController()
        fc.set_start_date("2024-05-01")
        fc.set_client("TechNova")
        params = fc.get_filter_params()
        self.assertEqual(params["start_date"], "2024-05-01")
        self.assertEqual(params["client_name"], "TechNova")
        self.assertIsNone(params["end_date"])

    def test_clear_dates_keeps_client(self):
        fc = FilterController()
        fc.set_start_date("2024-05-01")
        fc.set_client("TechNova")
        fc.clear_dates()
        self.assertIsNone(fc.start_date)
        self.assertEqual(fc.client_name, "TechNova")


class TestFilterControllerNotifications(unittest.TestCase):
    """Tests para sistema de notificaciones reactivas."""

    def test_on_change_called_on_set(self):
        fc = FilterController()
        fc.on_change = MagicMock()
        fc.set_start_date("2024-05-01")
        fc.on_change.assert_called_once()

    def test_suspend_prevents_callback(self):
        fc = FilterController()
        fc.on_change = MagicMock()
        fc.suspend_notifications()
        fc.start_date = "2024-05-01"
        fc._trigger_on_change()
        fc.on_change.assert_not_called()

    def test_resume_fires_pending(self):
        fc = FilterController()
        fc.on_change = MagicMock()
        fc.suspend_notifications()
        fc._trigger_on_change()
        fc.on_change.assert_not_called()
        fc.resume_notifications()
        fc.on_change.assert_called_once()

    def test_set_date_range_batches_notification(self):
        fc = FilterController()
        fc.on_change = MagicMock()
        fc.set_date_range("2024-05-01", "2024-05-31")
        # Solo una notificación (batch via suspend/resume)
        self.assertEqual(fc.on_change.call_count, 1)


if __name__ == "__main__":
    unittest.main()
