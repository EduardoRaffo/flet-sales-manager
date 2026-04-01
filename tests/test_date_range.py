"""
Tests para core/date_range.py - Validación de helpers de fecha.

Propósito: Congelar la semántica correcta de funciones de rango de fechas
para evitar regresiones futuras.
"""

import unittest
from datetime import date
from core.date_range import (
    current_month_full,
    current_year_full,
    current_month_to_date,
    current_year_to_date,
    last_n_days,
    current_week_full,
    current_quarter_full,
    current_quarter_to_date,
    previous_quarter_full,
    previous_year_full,
    same_quarter_previous_year,
    current_semester_full,
    previous_semester_full,
    current_semester_to_date,
    _to_iso,
    previous_month_full,
)


class TestDateRangeHelpers(unittest.TestCase):
    """Tests para validar la semántica de helpers de fecha."""

    # Fecha fija para tests deterministas (15 de mayo de 2024)
    FIXED_DATE = date(2024, 5, 15)

    # ====================================================================
    #   TESTS PARA current_month_full
    # ====================================================================

    def test_month_range_returns_calendar_month(self):
        """current_month_full devuelve el mes calendario completo (día 1 al último)."""
        start, end = current_month_full(today=self.FIXED_DATE)
        
        # Esperado: mayo 2024 completo (1-31)
        self.assertEqual(start, "2024-05-01", "current_month_full debe empezar el día 1")
        self.assertEqual(end, "2024-05-31", "current_month_full debe terminar el último día")

    def test_month_range_february_non_leap_year(self):
        """current_month_full para febrero en año no bisiesto (28 días)."""
        feb_date = date(2023, 2, 10)
        start, end = current_month_full(today=feb_date)
        
        self.assertEqual(start, "2023-02-01")
        self.assertEqual(end, "2023-02-28", "Febrero 2023 tiene 28 días")

    def test_month_range_february_leap_year(self):
        """current_month_full para febrero en año bisiesto (29 días)."""
        feb_date = date(2024, 2, 10)
        start, end = current_month_full(today=feb_date)
        
        self.assertEqual(start, "2024-02-01")
        self.assertEqual(end, "2024-02-29", "Febrero 2024 tiene 29 días (bisiesto)")

    def test_month_range_31_days_month(self):
        """current_month_full para meses con 31 días."""
        dec_date = date(2024, 12, 25)
        start, end = current_month_full(today=dec_date)
        
        self.assertEqual(start, "2024-12-01")
        self.assertEqual(end, "2024-12-31", "Diciembre tiene 31 días")

    def test_month_range_30_days_month(self):
        """current_month_full para meses con 30 días."""
        apr_date = date(2024, 4, 10)
        start, end = current_month_full(today=apr_date)
        
        self.assertEqual(start, "2024-04-01")
        self.assertEqual(end, "2024-04-30", "Abril tiene 30 días")

    def test_month_range_does_not_depend_on_day(self):
        """current_month_full devuelve el mismo rango sin importar el día del mes."""
        may_1 = current_month_full(today=date(2024, 5, 1))
        may_15 = current_month_full(today=date(2024, 5, 15))
        may_31 = current_month_full(today=date(2024, 5, 31))
        
        # Todos deben devolver el mismo rango (mayo completo)
        self.assertEqual(may_1, may_15)
        self.assertEqual(may_15, may_31)
        self.assertEqual(may_1, ("2024-05-01", "2024-05-31"))

    # ====================================================================
    #   TESTS PARA current_year_full
    # ====================================================================

    def test_year_range_returns_calendar_year(self):
        """current_year_full devuelve el año calendario completo (1 ene a 31 dic)."""
        start, end = current_year_full(today=self.FIXED_DATE)
        
        # Esperado: 2024 completo
        self.assertEqual(start, "2024-01-01", "current_year_full debe empezar el 1 de enero")
        self.assertEqual(end, "2024-12-31", "current_year_full debe terminar el 31 de diciembre")

    def test_year_range_different_years(self):
        """current_year_full funciona correctamente para diferentes años."""
        year_2023 = current_year_full(today=date(2023, 6, 15))
        year_2025 = current_year_full(today=date(2025, 12, 25))
        
        self.assertEqual(year_2023, ("2023-01-01", "2023-12-31"))
        self.assertEqual(year_2025, ("2025-01-01", "2025-12-31"))

    def test_year_range_does_not_depend_on_month_or_day(self):
        """current_year_full devuelve el mismo rango sin importar mes/día."""
        year_jan_1 = current_year_full(today=date(2024, 1, 1))
        year_jun_15 = current_year_full(today=date(2024, 6, 15))
        year_dec_31 = current_year_full(today=date(2024, 12, 31))
        
        # Todos deben devolver el mismo rango (2024 completo)
        self.assertEqual(year_jan_1, year_jun_15)
        self.assertEqual(year_jun_15, year_dec_31)
        self.assertEqual(year_jan_1, ("2024-01-01", "2024-12-31"))

    # ====================================================================
    #   TESTS PARA current_month_to_date (validar docstring)
    # ====================================================================

    def test_month_to_date_starts_day_1_ends_today(self):
        """current_month_to_date devuelve desde el 1 del mes hasta hoy."""
        start, end = current_month_to_date(today=self.FIXED_DATE)  # 2024-05-15
        
        self.assertEqual(start, "2024-05-01", "Debe empezar el 1 del mes")
        self.assertEqual(end, "2024-05-15", "Debe terminar en el día actual (hoy)")

    def test_month_to_date_first_day_of_month(self):
        """current_month_to_date cuando hoy es el primer día del mes."""
        first_day = current_month_to_date(today=date(2024, 5, 1))
        
        self.assertEqual(first_day, ("2024-05-01", "2024-05-01"),
                         "Si hoy es el 1, ambas fechas deben ser iguales")

    def test_month_to_date_last_day_of_month(self):
        """current_month_to_date cuando hoy es el último día del mes."""
        last_day = current_month_to_date(today=date(2024, 5, 31))
        
        self.assertEqual(last_day[0], "2024-05-01", "Debe empezar el 1")
        self.assertEqual(last_day[1], "2024-05-31", "Debe terminar el último día")

    # ====================================================================
    #   TESTS PARA current_year_to_date (validar docstring)
    # ====================================================================

    def test_year_to_date_starts_jan_1_ends_today(self):
        """current_year_to_date devuelve desde 1 enero hasta hoy."""
        start, end = current_year_to_date(today=self.FIXED_DATE)  # 2024-05-15
        
        self.assertEqual(start, "2024-01-01", "Debe empezar el 1 de enero")
        self.assertEqual(end, "2024-05-15", "Debe terminar en el día actual (hoy)")

    def test_year_to_date_first_day_of_year(self):
        """current_year_to_date cuando hoy es el 1 de enero."""
        first_day = current_year_to_date(today=date(2024, 1, 1))
        
        self.assertEqual(first_day, ("2024-01-01", "2024-01-01"),
                         "Si hoy es 1 enero, ambas fechas deben ser iguales")

    def test_year_to_date_last_day_of_year(self):
        """current_year_to_date cuando hoy es el 31 de diciembre."""
        last_day = current_year_to_date(today=date(2024, 12, 31))
        
        self.assertEqual(last_day[0], "2024-01-01", "Debe empezar el 1 de enero")
        self.assertEqual(last_day[1], "2024-12-31", "Debe terminar el 31 de diciembre")

    # ====================================================================
    #   TESTS ADICIONALES: Diferencias entre _range y _to_date
    # ====================================================================

    def test_month_range_vs_month_to_date_difference(self):
        """current_month_full y current_month_to_date son semánticamente diferentes."""
        test_date = date(2024, 5, 15)
        
        range_result = current_month_full(today=test_date)
        to_date_result = current_month_to_date(today=test_date)
        
        # month_range: mes completo (1-31)
        self.assertEqual(range_result, ("2024-05-01", "2024-05-31"))
        
        # month_to_date: inicio de mes hasta hoy (1-15)
        self.assertEqual(to_date_result, ("2024-05-01", "2024-05-15"))
        
        # Confirmación: END son diferentes
        self.assertNotEqual(range_result[1], to_date_result[1],
                           "current_month_full y current_month_to_date deben tener fin diferente")

    def test_year_range_vs_year_to_date_difference(self):
        """current_year_full y current_year_to_date son semánticamente diferentes."""
        test_date = date(2024, 5, 15)
        
        range_result = current_year_full(today=test_date)
        to_date_result = current_year_to_date(today=test_date)
        
        # year_range: año completo (1 ene - 31 dic)
        self.assertEqual(range_result, ("2024-01-01", "2024-12-31"))
        
        # year_to_date: inicio de año hasta hoy (1 ene - 15 may)
        self.assertEqual(to_date_result, ("2024-01-01", "2024-05-15"))
        
        # Confirmación: END son diferentes
        self.assertNotEqual(range_result[1], to_date_result[1],
                           "current_year_full y current_year_to_date deben tener fin diferente")

    # ====================================================================
    #   TESTS DE COMPATIBILIDAD CON OTROS HELPERS
    # ====================================================================

    def test_quick_range_semantics(self):
        """Validar que last_n_days devuelve últimos N días incluyendo hoy."""
        # Últimos 7 días incluyendo hoy (2024-05-15)
        start, end = last_n_days(days=7, today=self.FIXED_DATE)
        
        self.assertEqual(end, "2024-05-15", "Debe terminar en hoy")
        self.assertEqual(start, "2024-05-09", "7 días atrás desde 2024-05-15")

    def test_current_week_returns_mon_to_sun(self):
        """current_week_full devuelve lunes a domingo de la semana actual."""
        # 2024-05-15 es un miércoles, semana del 13-19 de mayo
        start, end = current_week_full(today=self.FIXED_DATE)
        
        self.assertEqual(start, "2024-05-13", "Debe ser lunes de la semana")
        self.assertEqual(end, "2024-05-19", "Debe ser domingo de la semana")

    def test_all_helpers_return_iso_format(self):
        """Todos los helpers devuelven tuplas con formato ISO (YYYY-MM-DD)."""
        helpers = [
            current_month_full(today=self.FIXED_DATE),
            current_year_full(today=self.FIXED_DATE),
            current_month_to_date(today=self.FIXED_DATE),
            current_year_to_date(today=self.FIXED_DATE),
            last_n_days(days=7, today=self.FIXED_DATE),
            current_week_full(today=self.FIXED_DATE),
            current_quarter_full(today=self.FIXED_DATE),
            current_semester_full(today=self.FIXED_DATE),
        ]
        
        for helper_result in helpers:
            self.assertIsInstance(helper_result, tuple)
            self.assertEqual(len(helper_result), 2)
            start, end = helper_result
            
            # Validar formato ISO YYYY-MM-DD
            self.assertRegex(start, r"^\d{4}-\d{2}-\d{2}$",
                           f"Start debe ser ISO: {start}")
            self.assertRegex(end, r"^\d{4}-\d{2}-\d{2}$",
                           f"End debe ser ISO: {end}")
            
            # Validar que start <= end
            self.assertLessEqual(start, end,
                               f"Start debe ser <= End: {start} vs {end}")
    def test_current_quarter_to_date(self):
      start, end = current_quarter_to_date(today=date(2026, 2, 10))
      self.assertEqual(start, "2026-01-01")
      self.assertEqual(end, "2026-02-10")


    def test_previous_quarter_full(self):
      start, end = previous_quarter_full(today=date(2026, 1, 15))
      self.assertEqual(start, "2025-10-01")
      self.assertEqual(end, "2025-12-31")


    def test_same_quarter_previous_year(self):
      start, end = same_quarter_previous_year(today=date(2026, 5, 10))
      self.assertEqual(start, "2025-04-01")
      self.assertEqual(end, "2025-06-30")

    def test_previous_month_full_mid_year(self):
        start, end = previous_month_full(today=date(2024, 5, 15))
        self.assertEqual(start, "2024-04-01")
        self.assertEqual(end, "2024-04-30")


    def test_previous_month_full_january(self):
            start, end = previous_month_full(today=date(2024, 1, 10))
            self.assertEqual(start, "2023-12-01")
            self.assertEqual(end, "2023-12-31")

    def test_previous_year_full(self):
        start, end = previous_year_full(today=date(2026, 5, 10))
        self.assertEqual(start, "2025-01-01")
        self.assertEqual(end, "2025-12-31")
    
    def test_current_semester_to_date_s1():
        start, end = current_semester_to_date(today=date(2026, 2, 10))
        assert start == "2026-01-01"
        assert end == "2026-02-10"



    def test_current_semester_to_date_s1(self):
        start, end = current_semester_to_date(today=date(2026, 2, 10))
        self.assertEqual(start, "2026-01-01")
        self.assertEqual(end, "2026-02-10")

    def test_current_semester_to_date_s2(self):
        start, end = current_semester_to_date(today=date(2026, 10, 5))
        self.assertEqual(start, "2026-07-01")
        self.assertEqual(end, "2026-10-05")

    def test_previous_semester_full_from_s1(self):
        start, end = previous_semester_full(today=date(2026, 2, 10))
        self.assertEqual(start, "2025-07-01")
        self.assertEqual(end, "2025-12-31")

    def test_previous_semester_full_from_s2(self):
        start, end = previous_semester_full(today=date(2026, 10, 5))
        self.assertEqual(start, "2026-01-01")
        self.assertEqual(end, "2026-06-30")
if __name__ == "__main__":
    unittest.main()
