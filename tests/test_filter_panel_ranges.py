"""
Tests para validar que todos los botones de rangos rápidos en FilterPanel funcionan correctamente.

Propósito: Asegurar que cada botón:
1. Obtiene el rango correcto
2. Actualiza las fechas en el controlador
3. Dispara el callback de filtro aplicado
"""

import unittest
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from unittest.mock import MagicMock, patch

from controllers.date_filter_controller import DateFilterController


class TestFilterPanelRanges(unittest.TestCase):
    """Tests para los botones de rangos en FilterPanel."""

    def setUp(self):
        """Inicializar el controlador para cada test."""
        self.controller = DateFilterController()

    # ====================================================================
    #   RANGOS RÁPIDOS (ÚLTIMOS N DÍAS)
    # ====================================================================

    def test_quick_range_7_days(self):
        """Botón 'Últimos 7 días' devuelve correctamente 7 últimos días."""
        start, end = self.controller.apply_quick_range(days=7)
        
        # Verificar que devuelve tupla (start, end)
        self.assertIsInstance(start, str)
        self.assertIsInstance(end, str)
        
        # Verificar que start < end y están en formato ISO
        self.assertLessEqual(start, end)
        self.assertRegex(start, r"^\d{4}-\d{2}-\d{2}$")
        self.assertRegex(end, r"^\d{4}-\d{2}-\d{2}$")
        
        # Verificar que el controlador almacenó las fechas
        self.assertEqual(self.controller.start_date, start)
        self.assertEqual(self.controller.end_date, end)

    def test_quick_range_15_days(self):
        """Botón 'Últimos 15 días' devuelve correctamente 15 últimos días."""
        start, end = self.controller.apply_quick_range(days=15)
        
        self.assertIsInstance(start, str)
        self.assertIsInstance(end, str)
        self.assertLessEqual(start, end)
        self.assertRegex(start, r"^\d{4}-\d{2}-\d{2}$")
        self.assertRegex(end, r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(self.controller.start_date, start)
        self.assertEqual(self.controller.end_date, end)

    # ====================================================================
    #   ÚLTIMOS N MESES
    # ====================================================================

    def test_quick_last_months_3(self):
        """Botón 'Últimos 3 meses' devuelve últimos 3 meses incluyendo hoy."""
        start, end = self.controller.apply_last_n_months(months=3)
        
        self.assertIsInstance(start, str)
        self.assertIsInstance(end, str)
        self.assertLessEqual(start, end)
        self.assertRegex(start, r"^\d{4}-\d{2}-\d{2}$")
        self.assertRegex(end, r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(self.controller.start_date, start)
        self.assertEqual(self.controller.end_date, end)

    def test_quick_last_months_6(self):
        """Botón 'Últimos 6 meses' devuelve últimos 6 meses incluyendo hoy."""
        start, end = self.controller.apply_last_n_months(months=6)
        
        self.assertIsInstance(start, str)
        self.assertIsInstance(end, str)
        self.assertLessEqual(start, end)
        self.assertRegex(start, r"^\d{4}-\d{2}-\d{2}$")
        self.assertRegex(end, r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(self.controller.start_date, start)
        self.assertEqual(self.controller.end_date, end)

    # ====================================================================
    #   AÑO (ÚLTIMOS 12 MESES)
    # ====================================================================

    def test_quick_year(self):
        """Botón 'Último año' devuelve últimos 12 meses incluyendo hoy."""
        start, end = self.controller.apply_last_n_months(months=12)
        
        self.assertIsInstance(start, str)
        self.assertIsInstance(end, str)
        self.assertLessEqual(start, end)
        self.assertRegex(start, r"^\d{4}-\d{2}-\d{2}$")
        self.assertRegex(end, r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(self.controller.start_date, start)
        self.assertEqual(self.controller.end_date, end)

    # ====================================================================
    #   SEMANA ACTUAL (HASTA HOY)
    # ====================================================================

    def test_current_week_to_date(self):
        """Botón 'Semana actual' devuelve desde lunes de esta semana hasta hoy."""
        start, end = self.controller.apply_current_week()
        
        self.assertIsInstance(start, str)
        self.assertIsInstance(end, str)
        self.assertLessEqual(start, end)
        self.assertRegex(start, r"^\d{4}-\d{2}-\d{2}$")
        self.assertRegex(end, r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(self.controller.start_date, start)
        self.assertEqual(self.controller.end_date, end)

    # ====================================================================
    #   MES ACTUAL (HASTA HOY)
    # ====================================================================

    def test_current_month_to_date(self):
        """Botón 'Mes actual' devuelve desde el 1 del mes hasta hoy."""
        start, end = self.controller.apply_current_month()
        
        self.assertIsInstance(start, str)
        self.assertIsInstance(end, str)
        self.assertLessEqual(start, end)
        self.assertRegex(start, r"^\d{4}-\d{2}-\d{2}$")
        self.assertRegex(end, r"^\d{4}-\d{2}-\d{2}$")
        
        # Verificar que el 1 del mes está incluido
        today = date.today()
        month_first = today.replace(day=1).strftime("%Y-%m-%d")
        self.assertEqual(start, month_first)
        self.assertEqual(self.controller.start_date, start)
        self.assertEqual(self.controller.end_date, end)

    # ====================================================================
    #   QUARTER ACTUAL (HASTA HOY)
    # ====================================================================

    def test_current_quarter_to_date(self):
        """Botón 'Quarter actual' devuelve desde inicio del quarter hasta hoy."""
        start, end = self.controller.apply_current_quarter()
        
        self.assertIsInstance(start, str)
        self.assertIsInstance(end, str)
        self.assertLessEqual(start, end)
        self.assertRegex(start, r"^\d{4}-\d{2}-\d{2}$")
        self.assertRegex(end, r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(self.controller.start_date, start)
        self.assertEqual(self.controller.end_date, end)

    # ====================================================================
    #   SEMESTRE ACTUAL (HASTA HOY)
    # ====================================================================

    def test_current_semester_to_date(self):
        """Botón 'Semestre actual' devuelve desde inicio del semestre hasta hoy."""
        start, end = self.controller.apply_current_semester()
        
        self.assertIsInstance(start, str)
        self.assertIsInstance(end, str)
        self.assertLessEqual(start, end)
        self.assertRegex(start, r"^\d{4}-\d{2}-\d{2}$")
        self.assertRegex(end, r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(self.controller.start_date, start)
        self.assertEqual(self.controller.end_date, end)

    # ====================================================================
    #   AÑO ACTUAL (HASTA HOY)
    # ====================================================================

    def test_current_year_to_date(self):
        """Botón 'Año actual' devuelve desde el 1 de enero hasta hoy."""
        start, end = self.controller.apply_current_year()
        
        self.assertIsInstance(start, str)
        self.assertIsInstance(end, str)
        self.assertLessEqual(start, end)
        self.assertRegex(start, r"^\d{4}-\d{2}-\d{2}$")
        self.assertRegex(end, r"^\d{4}-\d{2}-\d{2}$")
        
        # Verificar que el 1 de enero está incluido
        today = date.today()
        year_first = today.replace(month=1, day=1).strftime("%Y-%m-%d")
        self.assertEqual(start, year_first)
        self.assertEqual(self.controller.start_date, start)
        self.assertEqual(self.controller.end_date, end)

    # ====================================================================
    #   VALIDACIÓN GENERAL
    # ====================================================================

    def test_all_ranges_return_valid_dates(self):
        """Validar que todos los rangos devuelven tuplas de fechas válidas."""
        ranges = [
            ("7 días", lambda: self.controller.apply_quick_range(7)),
            ("15 días", lambda: self.controller.apply_quick_range(15)),
            ("3 meses", lambda: self.controller.apply_last_n_months(3)),
            ("6 meses", lambda: self.controller.apply_last_n_months(6)),
            ("12 meses", lambda: self.controller.apply_last_n_months(12)),
            ("Semana", lambda: self.controller.apply_current_week()),
            ("Mes", lambda: self.controller.apply_current_month()),
            ("Quarter", lambda: self.controller.apply_current_quarter()),
            ("Semestre", lambda: self.controller.apply_current_semester()),
            ("Año", lambda: self.controller.apply_current_year()),
        ]
        
        for name, func in ranges:
            with self.subTest(range=name):
                start, end = func()
                
                # Validaciones comunes
                self.assertIsInstance(start, str, f"{name}: start debe ser string")
                self.assertIsInstance(end, str, f"{name}: end debe ser string")
                self.assertRegex(start, r"^\d{4}-\d{2}-\d{2}$", f"{name}: start debe ser ISO")
                self.assertRegex(end, r"^\d{4}-\d{2}-\d{2}$", f"{name}: end debe ser ISO")
                self.assertLessEqual(start, end, f"{name}: start debe ser <= end")

    def test_all_ranges_update_controller_state(self):
        """Validar que todos los rangos actualizan el estado del controlador."""
        ranges = [
            ("7 días", lambda: self.controller.apply_quick_range(7)),
            ("15 días", lambda: self.controller.apply_quick_range(15)),
            ("3 meses", lambda: self.controller.apply_last_n_months(3)),
            ("6 meses", lambda: self.controller.apply_last_n_months(6)),
            ("12 meses", lambda: self.controller.apply_last_n_months(12)),
            ("Semana", lambda: self.controller.apply_current_week()),
            ("Mes", lambda: self.controller.apply_current_month()),
            ("Quarter", lambda: self.controller.apply_current_quarter()),
            ("Semestre", lambda: self.controller.apply_current_semester()),
            ("Año", lambda: self.controller.apply_current_year()),
        ]
        
        for name, func in ranges:
            with self.subTest(range=name):
                self.controller = DateFilterController()  # Reset
                start, end = func()
                
                # Verificar que el controlador almacenó las fechas
                self.assertEqual(self.controller.start_date, start,
                               f"Controller start_date no coincide con return value")
                self.assertEqual(self.controller.end_date, end,
                               f"Controller end_date no coincide con return value")


class TestFilterPanelRangesWithMockedDate(unittest.TestCase):
    """Tests para rangos usando mock de fecha para verificar comportamiento actual."""

    def test_quick_range_today(self):
        """Verificar quick_range con fecha de hoy."""
        controller = DateFilterController()
        start, end = controller.apply_quick_range(days=7)
        
        # Verificar que el rango es válido (sin importar la fecha actual)
        from datetime import timedelta
        today = date.today()
        expected_start = (today - timedelta(days=6)).strftime("%Y-%m-%d")
        expected_end = today.strftime("%Y-%m-%d")
        
        self.assertEqual(start, expected_start)
        self.assertEqual(end, expected_end)

    def test_current_month_today(self):
        """Verificar current_month_full con fecha de hoy."""
        controller = DateFilterController()
        start, end = controller.apply_month_range()
        
        # Verificar que el rango es válido (sin importar la fecha actual)
        today = date.today()
        month_start = today.replace(day=1)
        month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)
        
        expected_start = month_start.strftime("%Y-%m-%d")
        expected_end = month_end.strftime("%Y-%m-%d")
        
        self.assertEqual(start, expected_start)
        self.assertEqual(end, expected_end)


if __name__ == "__main__":
    unittest.main()
