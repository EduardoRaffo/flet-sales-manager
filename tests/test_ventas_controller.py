"""
Tests para controllers/ventas_controller.py — Controlador de ventas.
"""

import unittest
from unittest.mock import patch, MagicMock
from controllers.ventas_controller import VentasController
from controllers.compare_controller import CompareController


class TestGroupingNormalization(unittest.TestCase):
    """Tests para normalización defensiva de grouping en get_sales_snapshot."""

    def setUp(self):
        self.ctrl = VentasController()

    @patch("analysis.get_sales_summary", return_value=(None, None))
    def test_valid_grouping_passes(self, mock_summary):
        """Grouping válido no se modifica (pero retorna None porque df es None)."""
        result = self.ctrl.get_sales_snapshot(grouping="month")
        self.assertIsNone(result)

    @patch("analysis.get_sales_summary", return_value=(None, None))
    def test_invalid_grouping_defaults_to_day(self, mock_summary):
        """Grouping inválido se normaliza a 'day'."""
        result = self.ctrl.get_sales_snapshot(grouping="invalid")
        self.assertIsNone(result)

    @patch("analysis.get_sales_summary", return_value=(None, None))
    def test_non_string_grouping_defaults_to_day(self, mock_summary):
        """Grouping no-string se normaliza a 'day'."""
        result = self.ctrl.get_sales_snapshot(grouping=123)
        self.assertIsNone(result)


class TestSnapshotCache(unittest.TestCase):
    """Tests para el sistema de caché de snapshots."""

    def setUp(self):
        self.ctrl = VentasController()

    def test_build_snapshot_key_deterministic(self):
        key1 = self.ctrl.build_snapshot_key("2024-01-01", "2024-06-30", None, None, "day")
        key2 = self.ctrl.build_snapshot_key("2024-01-01", "2024-06-30", None, None, "day")
        self.assertEqual(key1, key2)

    def test_different_params_different_key(self):
        key1 = self.ctrl.build_snapshot_key("2024-01-01", "2024-06-30", None, None, "day")
        key2 = self.ctrl.build_snapshot_key("2024-01-01", "2024-06-30", "TechNova", None, "day")
        self.assertNotEqual(key1, key2)

    def test_invalidate_cache_clears_all(self):
        self.ctrl._snapshot_cache["key1"] = "snap1"
        self.ctrl._snapshot_cache["key2"] = "snap2"
        self.ctrl.invalidate_snapshot_cache()
        self.assertEqual(len(self.ctrl._snapshot_cache), 0)
        self.assertIsNone(self.ctrl._last_snapshot_key)

    def test_invalidate_increments_version(self):
        v0 = self.ctrl._dataset_version
        self.ctrl.invalidate_snapshot_cache()
        self.assertEqual(self.ctrl._dataset_version, v0 + 1)


class TestFilterDelegation(unittest.TestCase):
    """Tests para delegación de filtros a FilterController."""

    def setUp(self):
        self.ctrl = VentasController()

    def test_set_start_date(self):
        result = self.ctrl.set_start_date("2024-05-01")
        params = self.ctrl.get_filter_params()
        self.assertEqual(params["start_date"], "2024-05-01")

    def test_apply_quick_range(self):
        start, end = self.ctrl.apply_quick_range(30)
        self.assertIsNotNone(start)
        self.assertIsNotNone(end)

    def test_validate_filters_default(self):
        ok, msg = self.ctrl.validate_filters()
        self.assertTrue(ok)

    def test_clear_filters(self):
        self.ctrl.set_start_date("2024-01-01")
        self.ctrl.clear_filters()
        params = self.ctrl.get_filter_params()
        self.assertIsNone(params["start_date"])


class TestViewMode(unittest.TestCase):
    """Tests para set_view_mode."""

    def setUp(self):
        self.ctrl = VentasController()

    def test_summary_mode(self):
        self.ctrl.set_view_mode("summary")
        self.assertEqual(self.ctrl.current_view_mode, "summary")

    def test_both_mode(self):
        self.ctrl.set_view_mode("both")
        self.assertEqual(self.ctrl.current_view_mode, "both")

    def test_invalid_mode_ignored(self):
        self.ctrl.set_view_mode("both")
        self.ctrl.set_view_mode("invalid")
        self.assertEqual(self.ctrl.current_view_mode, "both")


class TestCompareGrouping(unittest.TestCase):
    """Tests para el flujo de agrupacion en modo compare."""

    def setUp(self):
        self.ctrl = VentasController()

    @patch("controllers.ventas_controller.build_sales_snapshot")
    @patch("controllers.ventas_controller.build_period_data")
    @patch("analysis.get_sales_summary")
    def test_compare_snapshot_uses_controller_grouping(
        self,
        mock_get_summary,
        mock_build_period_data,
        mock_build_snapshot,
    ):
        mock_df = MagicMock()
        mock_df.is_empty.return_value = False
        mock_get_summary.side_effect = [(mock_df, None), (mock_df, None)]
        mock_build_period_data.return_value = {}

        snapshot = MagicMock()
        snapshot.validate.return_value = True
        snapshot.is_compare_mode.return_value = True
        snapshot.comparison = MagicMock()
        mock_build_snapshot.return_value = snapshot

        compare = CompareController()
        compare.set_period_a("2024-05-01", "2024-05-31")
        compare.set_period_b("2024-04-01", "2024-04-30")
        compare.set_grouping("month")
        compare.activate_compare()

        result = self.ctrl.get_sales_snapshot(grouping="month", compare_controller=compare)

        self.assertIs(result, snapshot)
        self.assertEqual(mock_build_period_data.call_count, 2)
        for call in mock_build_period_data.call_args_list:
            self.assertEqual(call.kwargs["grouping"], "month")
            self.assertTrue(call.kwargs["is_compare"])


if __name__ == "__main__":
    unittest.main()
