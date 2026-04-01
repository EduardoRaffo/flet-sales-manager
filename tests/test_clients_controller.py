"""
Tests para controllers/clients_controller.py — Gestión de clientes.
"""

import unittest
from unittest.mock import patch, MagicMock


class TestValidateClientFields(unittest.TestCase):
    """Tests para ClientsController.validate_client_fields()."""

    def setUp(self):
        from controllers.clients_controller import ClientsController
        self.ctrl = ClientsController

    def test_valid_fields(self):
        ok, msg = self.ctrl.validate_client_fields("TechNova", "B12345678", "info@tech.com", "Juan")
        self.assertTrue(ok)
        self.assertEqual(msg, "")

    def test_name_too_short(self):
        ok, msg = self.ctrl.validate_client_fields("A", "B12345678", "a@b.com", "Juan")
        self.assertFalse(ok)
        self.assertIn("nombre", msg.lower())

    def test_cif_invalid(self):
        ok, msg = self.ctrl.validate_client_fields("TechNova", "AB", "a@b.com", "Juan")
        self.assertFalse(ok)
        self.assertIn("CIF", msg)

    def test_email_invalid(self):
        ok, msg = self.ctrl.validate_client_fields("TechNova", "B12345678", "not-email", "Juan")
        self.assertFalse(ok)
        self.assertIn("email", msg.lower())

    def test_contact_too_short(self):
        ok, msg = self.ctrl.validate_client_fields("TechNova", "B12345678", "a@b.com", "J")
        self.assertFalse(ok)
        self.assertIn("contacto", msg.lower())

    def test_none_name(self):
        ok, msg = self.ctrl.validate_client_fields(None, "B12345678", "a@b.com", "Juan")
        self.assertFalse(ok)

    def test_empty_cif_accepted(self):
        """CIF vacío es aceptado (campo opcional)."""
        ok, msg = self.ctrl.validate_client_fields("TechNova", "", "a@b.com", "Juan")
        self.assertTrue(ok)

    def test_none_email_accepted(self):
        """Email None podría ser aceptado o rechazado según validate_email."""
        ok, msg = self.ctrl.validate_client_fields("TechNova", "B12345678", None, "Juan")
        # Solo verificamos que no lanza excepción
        self.assertIsInstance(ok, bool)


class TestCreateClient(unittest.TestCase):
    """Tests para ClientsController.create_client()."""

    @patch("controllers.clients_controller.add_client")
    @patch("controllers.clients_controller.client_exists_by_name", return_value=False)
    @patch("controllers.clients_controller.client_exists_by_cif", return_value=False)
    def test_success(self, mock_cif, mock_name, mock_add):
        from controllers.clients_controller import ClientsController
        ok, msg = ClientsController.create_client("TechNova", "B12345678", "Calle 1", "Juan", "a@b.com")
        self.assertTrue(ok)
        mock_add.assert_called_once()

    @patch("controllers.clients_controller.client_exists_by_cif", return_value=True)
    def test_duplicate_cif(self, mock_cif):
        from controllers.clients_controller import ClientsController
        ok, msg = ClientsController.create_client("TechNova", "B12345678", "Calle 1", "Juan", "a@b.com")
        self.assertFalse(ok)
        self.assertIn("CIF", msg)

    @patch("controllers.clients_controller.client_exists_by_cif", return_value=False)
    @patch("controllers.clients_controller.client_exists_by_name", return_value=True)
    def test_duplicate_name(self, mock_name, mock_cif):
        from controllers.clients_controller import ClientsController
        ok, msg = ClientsController.create_client("TechNova", "B12345678", "Calle 1", "Juan", "a@b.com")
        self.assertFalse(ok)
        self.assertIn("nombre", msg.lower())

    def test_validation_fails(self):
        from controllers.clients_controller import ClientsController
        ok, msg = ClientsController.create_client("A", "B12345678", "Calle 1", "Juan", "a@b.com")
        self.assertFalse(ok)


class TestUpdateClientInfo(unittest.TestCase):
    """Tests para ClientsController.update_client_info()."""

    @patch("controllers.clients_controller.update_client")
    @patch("controllers.clients_controller.get_client_by_id", return_value=("C001", "Old", "B12345678", "", "", ""))
    @patch("controllers.clients_controller.client_exists_by_name", return_value=False)
    @patch("controllers.clients_controller.client_exists_by_cif", return_value=False)
    def test_update_existing(self, mock_cif, mock_name, mock_get, mock_update):
        from controllers.clients_controller import ClientsController
        ok, msg = ClientsController.update_client_info("C001", "TechNova", "B12345678", "Calle 1", "Juan", "a@b.com")
        self.assertTrue(ok)
        mock_update.assert_called_once()

    @patch("controllers.clients_controller.add_client_with_id")
    @patch("controllers.clients_controller.get_client_by_id", return_value=None)
    @patch("controllers.clients_controller.client_exists_by_name", return_value=False)
    @patch("controllers.clients_controller.client_exists_by_cif", return_value=False)
    def test_creates_if_not_exists(self, mock_cif, mock_name, mock_get, mock_add):
        from controllers.clients_controller import ClientsController
        ok, msg = ClientsController.update_client_info("C099", "NewCo", "B99999999", "Calle 9", "Ana", "ana@co.com")
        self.assertTrue(ok)
        mock_add.assert_called_once()


class TestRemoveClient(unittest.TestCase):
    """Tests para ClientsController.remove_client()."""

    @patch("controllers.clients_controller.delete_client")
    @patch("controllers.clients_controller.get_client_by_id_cached", return_value=("C001", "TechNova", "B123", "", "", ""))
    def test_success(self, mock_find, mock_delete):
        from controllers.clients_controller import ClientsController
        ok, msg = ClientsController.remove_client("C001")
        self.assertTrue(ok)
        self.assertIn("TechNova", msg)

    @patch("controllers.clients_controller.get_client_by_id_cached", return_value=None)
    @patch("controllers.clients_controller.get_all_clients_with_sales_data", return_value=[])
    def test_not_found(self, mock_all, mock_find):
        from controllers.clients_controller import ClientsController
        ok, msg = ClientsController.remove_client("C999")
        self.assertFalse(ok)
        self.assertIn("no encontrado", msg.lower())


class TestSearchClientsByName(unittest.TestCase):
    """Tests para ClientsController.search_clients_by_name()."""

    CLIENTS = [
        {"client_id": "C001", "name": "TechNova"},
        {"client_id": "C002", "name": "DataCorp"},
        {"client_id": "C003", "name": "CloudSoft"},
    ]

    @patch("controllers.clients_controller.get_all_clients_with_sales_data")
    def test_empty_returns_all(self, mock_all):
        mock_all.return_value = self.CLIENTS
        from controllers.clients_controller import ClientsController
        result = ClientsController.search_clients_by_name("")
        self.assertEqual(len(result), 3)

    @patch("controllers.clients_controller.get_all_clients_with_sales_data")
    def test_partial_case_insensitive(self, mock_all):
        mock_all.return_value = self.CLIENTS
        from controllers.clients_controller import ClientsController
        result = ClientsController.search_clients_by_name("tech")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "TechNova")

    @patch("controllers.clients_controller.get_all_clients_with_sales_data")
    def test_no_match(self, mock_all):
        mock_all.return_value = self.CLIENTS
        from controllers.clients_controller import ClientsController
        result = ClientsController.search_clients_by_name("XYZ")
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()
