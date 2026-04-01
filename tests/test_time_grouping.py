"""
Tests para analysis/time_grouping.py — Funciones puras de agrupación temporal.
"""

import unittest
from analysis.time_grouping import group_time_series, is_valid_regroup, GRANULARITY_LEVEL


class TestGroupTimeSeries(unittest.TestCase):
    """Tests para group_time_series()."""

    def test_empty_input_returns_empty(self):
        self.assertEqual(group_time_series([], "day"), [])

    def test_day_grouping(self):
        rows = [("2024-03-01", 100.0), ("2024-03-02", 200.0)]
        result = group_time_series(rows, "day")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["key"], "2024-03-01")
        self.assertEqual(result[0]["label"], "01/03")
        self.assertEqual(result[0]["total"], 100.0)

    def test_week_grouping(self):
        rows = [("2024-03-04", 100.0), ("2024-03-05", 200.0)]
        result = group_time_series(rows, "week")
        self.assertEqual(len(result), 1)
        self.assertIn("-W", result[0]["key"])
        self.assertIn("Sem", result[0]["label"])
        self.assertEqual(result[0]["total"], 300.0)

    def test_month_grouping(self):
        rows = [("2024-03-01", 100.0), ("2024-03-15", 200.0)]
        result = group_time_series(rows, "month")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["key"], "2024-03")
        self.assertEqual(result[0]["total"], 300.0)

    def test_quarter_grouping(self):
        rows = [("2024-01-15", 100.0), ("2024-03-20", 200.0)]
        result = group_time_series(rows, "quarter")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["key"], "2024-Q1")
        self.assertIn("Q1", result[0]["label"])
        self.assertEqual(result[0]["total"], 300.0)

    def test_year_grouping(self):
        rows = [("2024-01-15", 100.0), ("2024-12-20", 200.0)]
        result = group_time_series(rows, "year")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["key"], "2024")
        self.assertEqual(result[0]["total"], 300.0)

    def test_values_aggregated_same_group(self):
        """Valores del mismo mes se suman correctamente."""
        rows = [
            ("2024-05-01", 100.0),
            ("2024-05-10", 200.0),
            ("2024-05-20", 300.0),
        ]
        result = group_time_series(rows, "month")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["total"], 600.0)

    def test_multiple_groups(self):
        """Datos de diferentes meses se separan correctamente."""
        rows = [
            ("2024-03-01", 100.0),
            ("2024-04-01", 200.0),
            ("2024-05-01", 300.0),
        ]
        result = group_time_series(rows, "month")
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["key"], "2024-03")
        self.assertEqual(result[2]["key"], "2024-05")

    def test_sorted_by_key(self):
        """Resultado ordenado por clave temporal."""
        rows = [("2024-05-01", 100.0), ("2024-03-01", 200.0)]
        result = group_time_series(rows, "month")
        self.assertEqual(result[0]["key"], "2024-03")
        self.assertEqual(result[1]["key"], "2024-05")

    def test_invalid_grouping_raises(self):
        rows = [("2024-03-01", 100.0)]
        with self.assertRaises(ValueError):
            group_time_series(rows, "invalid")

    def test_malformed_date_skipped(self):
        """Fechas mal formadas se ignoran silenciosamente."""
        rows = [("bad-date", 100.0), ("2024-03-01", 200.0)]
        result = group_time_series(rows, "day")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["total"], 200.0)


class TestIsValidRegroup(unittest.TestCase):
    """Tests para is_valid_regroup()."""

    def test_same_grouping_valid(self):
        self.assertTrue(is_valid_regroup("day", "day"))

    def test_coarser_valid(self):
        self.assertTrue(is_valid_regroup("day", "month"))

    def test_day_to_year_valid(self):
        self.assertTrue(is_valid_regroup("day", "year"))

    def test_finer_invalid(self):
        self.assertFalse(is_valid_regroup("month", "day"))

    def test_invalid_grouping_returns_false(self):
        self.assertFalse(is_valid_regroup("invalid", "day"))

    def test_both_invalid_returns_false(self):
        self.assertFalse(is_valid_regroup("foo", "bar"))

    def test_week_to_month_valid(self):
        self.assertTrue(is_valid_regroup("week", "month"))

    def test_quarter_to_week_invalid(self):
        self.assertFalse(is_valid_regroup("quarter", "week"))


class TestGranularityLevel(unittest.TestCase):
    """Tests para la constante GRANULARITY_LEVEL."""

    def test_hierarchy_order(self):
        self.assertLess(GRANULARITY_LEVEL["day"], GRANULARITY_LEVEL["week"])
        self.assertLess(GRANULARITY_LEVEL["week"], GRANULARITY_LEVEL["month"])
        self.assertLess(GRANULARITY_LEVEL["month"], GRANULARITY_LEVEL["quarter"])
        self.assertLess(GRANULARITY_LEVEL["quarter"], GRANULARITY_LEVEL["year"])


if __name__ == "__main__":
    unittest.main()
