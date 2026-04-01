"""
Test de integración: Validar flujo de DateFilterController.

Este test valida que:
1. Los botones de FilterPanel llamen correctamente al controlador
2. El controlador calcule fechas correctamente
3. Las fechas se almacenen correctamente para pasar al siguiente nivel
"""

import unittest
from datetime import date
from controllers.date_filter_controller import DateFilterController


class TestDateFilterControllerIntegration(unittest.TestCase):
    """Test de integración: FilterPanel → DateFilterController (flujo de datos)"""

    def setUp(self):
        """Inicializar controlador."""
        self.controller = DateFilterController()

    def test_flow_quick_range_7_days_state(self):
        """
        Flujo: Usuario hace click en 'Últimos 7 días'
        Verificar que el estado se actualiza correctamente para pasar al siguiente nivel.
        """
        # Paso 1: Usuario hace click en botón
        start, end = self.controller.apply_quick_range(days=7)
        
        # Paso 2: Verificar que el estado se actualizó
        self.assertEqual(self.controller.start_date, start)
        self.assertEqual(self.controller.end_date, end)
        
        # Paso 3: Verificar que las fechas son válidas
        self.assertIsNotNone(start)
        self.assertIsNotNone(end)
        self.assertLessEqual(start, end)
        
        # Paso 4: Verificar formato ISO
        self.assertRegex(start, r"^\d{4}-\d{2}-\d{2}$")
        self.assertRegex(end, r"^\d{4}-\d{2}-\d{2}$")

    def test_flow_current_month_to_date_state(self):
        """
        Flujo: Usuario hace click en 'Mes actual'
        Verificar que el estado almacena: 1 del mes hasta hoy
        """
        # Paso 1: Usuario hace click en botón
        start, end = self.controller.apply_current_month()
        
        # Paso 2: Verificar que el estado se actualizó
        self.assertEqual(self.controller.start_date, start)
        self.assertEqual(self.controller.end_date, end)
        
        # Paso 3: Verificar que start es el 1 del mes
        today = date.today()
        expected_start = today.replace(day=1).strftime("%Y-%m-%d")
        self.assertEqual(start, expected_start)
        
        # Paso 4: Verificar que end es hoy
        expected_end = today.strftime("%Y-%m-%d")
        self.assertEqual(end, expected_end)

    def test_flow_last_6_months_state(self):
        """
        Flujo: Usuario hace click en 'Últimos 6 meses'
        Verificar que el estado almacena: hace 6 meses hasta hoy
        """
        # Paso 1: Usuario hace click en botón
        start, end = self.controller.apply_last_n_months(months=6)
        
        # Paso 2: Verificar que el estado se actualizó
        self.assertEqual(self.controller.start_date, start)
        self.assertEqual(self.controller.end_date, end)
        
        # Paso 3: Verificar que las fechas son válidas
        self.assertIsNotNone(start)
        self.assertIsNotNone(end)
        self.assertLessEqual(start, end)

    def test_flow_current_year_to_date_state(self):
        """
        Flujo: Usuario hace click en 'Año actual'
        Verificar que el estado almacena: 1 de enero hasta hoy
        """
        # Paso 1: Usuario hace click en botón
        start, end = self.controller.apply_current_year()
        
        # Paso 2: Verificar que el estado se actualizó
        self.assertEqual(self.controller.start_date, start)
        self.assertEqual(self.controller.end_date, end)
        
        # Paso 3: Verificar que start es el 1 de enero
        today = date.today()
        expected_start = today.replace(month=1, day=1).strftime("%Y-%m-%d")
        self.assertEqual(start, expected_start)
        
        # Paso 4: Verificar que end es hoy
        expected_end = today.strftime("%Y-%m-%d")
        self.assertEqual(end, expected_end)

    def test_all_range_buttons_update_state(self):
        """
        Test exhaustivo: Verificar que TODOS los botones actualizan el estado
        del controlador correctamente.
        """
        range_buttons = [
            ("apply_quick_range", {"days": 7}),
            ("apply_quick_range", {"days": 15}),
            ("apply_quick_range", {"days": 30}),
            ("apply_last_n_months", {"months": 3}),
            ("apply_last_n_months", {"months": 6}),
            ("apply_last_n_months", {"months": 12}),
            ("apply_current_week", {}),
            ("apply_current_month", {}),
            ("apply_current_quarter", {}),
            ("apply_current_semester", {}),
            ("apply_current_year", {}),
        ]
        
        for method_name, kwargs in range_buttons:
            with self.subTest(method=method_name, kwargs=kwargs):
                # Resetear controlador
                self.controller = DateFilterController()
                
                # Llamar al método
                method = getattr(self.controller, method_name)
                start, end = method(**kwargs)
                
                # Verificar que el estado se actualizó
                self.assertEqual(self.controller.start_date, start)
                self.assertEqual(self.controller.end_date, end)
                
                # Verificar que las fechas son válidas
                self.assertIsNotNone(start)
                self.assertIsNotNone(end)
                self.assertLessEqual(start, end)
                
                # Verificar formato ISO
                self.assertRegex(start, r"^\d{4}-\d{2}-\d{2}$")
                self.assertRegex(end, r"^\d{4}-\d{2}-\d{2}$")

    def test_controller_state_persistence(self):
        """
        Verificar que el estado persiste en el controlador después de aplicar un rango.
        """
        # Aplicar rango
        start1, end1 = self.controller.apply_quick_range(days=7)
        
        # Verificar estado
        self.assertEqual(self.controller.start_date, start1)
        self.assertEqual(self.controller.end_date, end1)
        
        # Aplicar otro rango
        start2, end2 = self.controller.apply_last_n_months(months=3)
        
        # Verificar que el estado se actualizó al nuevo rango
        self.assertEqual(self.controller.start_date, start2)
        self.assertEqual(self.controller.end_date, end2)
        
        # Verificar que es diferente del anterior
        self.assertNotEqual(start1, start2)

    def test_controller_validation(self):
        """Verificar que el controlador valida correctamente los rangos."""
        # Aplicar rango válido
        self.controller.apply_quick_range(days=7)
        
        # Validar
        is_valid, error = self.controller.validate()
        self.assertTrue(is_valid)
        self.assertIsNone(error)


if __name__ == "__main__":
    unittest.main()
