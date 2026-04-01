"""
Tests para utils/formatting.py — Funciones puras de formateo monetario.
"""

import unittest
from utils.formatting import format_eur, format_eur_no_symbol, format_eur_signed, mask_sensitive


class TestFormatEur(unittest.TestCase):
    """Tests para format_eur()."""

    def test_standard_format(self):
        self.assertEqual(format_eur(1234.56), "€ 1.234,56")

    def test_large_number(self):
        self.assertEqual(format_eur(1234567.89), "€ 1.234.567,89")

    def test_zero_decimals(self):
        self.assertEqual(format_eur(1234, decimals=0), "€ 1.234")

    def test_zero_value(self):
        self.assertEqual(format_eur(0), "€ 0,00")

    def test_negative_value(self):
        self.assertEqual(format_eur(-1234.56), "€ -1.234,56")

    def test_non_numeric_returns_default(self):
        self.assertEqual(format_eur("abc"), "€ 0,00")

    def test_none_returns_default(self):
        self.assertEqual(format_eur(None), "€ 0,00")

    def test_small_value(self):
        self.assertEqual(format_eur(0.5), "€ 0,50")

    def test_string_numeric_converted(self):
        self.assertEqual(format_eur("1234.56"), "€ 1.234,56")


class TestFormatEurNoSymbol(unittest.TestCase):
    """Tests para format_eur_no_symbol()."""

    def test_standard(self):
        self.assertEqual(format_eur_no_symbol(1234.56), "1.234,56")

    def test_non_numeric_returns_default(self):
        self.assertEqual(format_eur_no_symbol("abc"), "0,00")

    def test_zero_decimals(self):
        self.assertEqual(format_eur_no_symbol(1234, decimals=0), "1.234")


class TestFormatEurSigned(unittest.TestCase):
    """Tests para format_eur_signed()."""

    def test_positive_value(self):
        self.assertEqual(format_eur_signed(1234.56), "+1.234,56")

    def test_negative_value(self):
        result = format_eur_signed(-1234.56)
        self.assertIn("-1.234,56", result)
        self.assertNotIn("+-", result)

    def test_zero_value(self):
        self.assertEqual(format_eur_signed(0), "+0,00")

    def test_non_numeric_returns_default(self):
        self.assertEqual(format_eur_signed("abc"), "+0,00")


class TestMaskSensitive(unittest.TestCase):
    """Tests para mask_sensitive()."""

    def test_normal_value_masked(self):
        self.assertEqual(mask_sensitive("A12345678"), "••••••••")

    def test_none_passes_through(self):
        self.assertIsNone(mask_sensitive(None))

    def test_dash_passes_through(self):
        self.assertEqual(mask_sensitive("—"), "—")

    def test_hyphen_passes_through(self):
        self.assertEqual(mask_sensitive("-"), "-")

    def test_empty_string_passes_through(self):
        self.assertEqual(mask_sensitive(""), "")

    def test_email_masked(self):
        self.assertEqual(mask_sensitive("user@example.com"), "••••••••")


if __name__ == "__main__":
    unittest.main()
