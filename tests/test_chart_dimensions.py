"""
Tests para analysis/chart_dimensions.py — Funciones puras de cálculo visual.
"""

import unittest
from analysis.chart_dimensions import get_rod_width, get_label_interval, round_to_nice_number


class TestGetRodWidth(unittest.TestCase):
    """Tests para get_rod_width()."""

    def test_small_dataset_5(self):
        self.assertEqual(get_rod_width(5), 40)

    def test_boundary_7(self):
        self.assertEqual(get_rod_width(7), 40)

    def test_boundary_8(self):
        self.assertEqual(get_rod_width(8), 32)

    def test_boundary_15(self):
        self.assertEqual(get_rod_width(15), 32)

    def test_medium_dataset_25(self):
        self.assertEqual(get_rod_width(25), 24)

    def test_large_dataset_70(self):
        self.assertEqual(get_rod_width(70), 12)

    def test_very_large_dataset_100(self):
        self.assertEqual(get_rod_width(100), 12)

    def test_massive_dataset_150(self):
        self.assertEqual(get_rod_width(150), 8)


class TestGetLabelInterval(unittest.TestCase):
    """Tests para get_label_interval()."""

    def test_small_10(self):
        self.assertEqual(get_label_interval(10), 1)

    def test_boundary_15(self):
        self.assertEqual(get_label_interval(15), 1)

    def test_medium_25(self):
        self.assertEqual(get_label_interval(25), 2)

    def test_large_80(self):
        self.assertEqual(get_label_interval(80), 5)

    def test_massive_120(self):
        self.assertEqual(get_label_interval(120), 10)


class TestRoundToNiceNumber(unittest.TestCase):
    """Tests para round_to_nice_number()."""

    def test_small_value(self):
        self.assertEqual(round_to_nice_number(5), 10.0)

    def test_87(self):
        self.assertEqual(round_to_nice_number(87), 100.0)

    def test_234(self):
        self.assertEqual(round_to_nice_number(234), 250.0)

    def test_1567(self):
        self.assertEqual(round_to_nice_number(1567), 2000.0)

    def test_12345(self):
        self.assertEqual(round_to_nice_number(12345), 15000.0)

    def test_value_10(self):
        result = round_to_nice_number(10)
        self.assertGreaterEqual(result, 10.0)

    def test_value_100(self):
        result = round_to_nice_number(100)
        self.assertEqual(result, 150.0)

    def test_negative_small(self):
        """Valores < 10 retornan 10.0."""
        self.assertEqual(round_to_nice_number(3), 10.0)


if __name__ == "__main__":
    unittest.main()
