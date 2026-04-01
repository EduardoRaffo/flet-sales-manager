"""
Tests para controllers/file_import_controller.py — Importación de archivos.
"""

import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock, call
from controllers.file_import_controller import FileImportController


class TestValidateFile(unittest.TestCase):
    """Tests para FileImportController.validate_file()."""

    def setUp(self):
        self.ctrl = FileImportController(
            on_success=MagicMock(),
            on_error=MagicMock(),
            on_start=MagicMock(),
        )

    def test_none_path(self):
        ok, msg = self.ctrl.validate_file(None)
        self.assertFalse(ok)
        self.assertIn("seleccionó", msg.lower())

    def test_nonexistent_path(self):
        ok, msg = self.ctrl.validate_file("/no/existe/archivo.csv")
        self.assertFalse(ok)
        self.assertIn("no existe", msg.lower())

    def test_valid_path(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            f.write(b"col1,col2\n")
            path = f.name
        try:
            ok, msg = self.ctrl.validate_file(path)
            self.assertTrue(ok)
            self.assertIsNone(msg)
        finally:
            os.unlink(path)

    def test_empty_string_path(self):
        ok, msg = self.ctrl.validate_file("")
        self.assertFalse(ok)


class TestImportFile(unittest.TestCase):
    """Tests para FileImportController.import_file()."""

    def test_invalid_file_calls_on_error(self):
        on_success = MagicMock()
        on_error = MagicMock()
        on_start = MagicMock()
        ctrl = FileImportController(on_success, on_error, on_start)

        ctrl.import_file(None)
        on_error.assert_called_once()
        on_start.assert_not_called()

    def test_valid_file_calls_on_start(self):
        on_success = MagicMock()
        on_error = MagicMock()
        on_start = MagicMock()
        ctrl = FileImportController(on_success, on_error, on_start)

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            f.write(b"col1,col2\n")
            path = f.name
        try:
            with patch("controllers.file_import_controller.import_csv_to_db", return_value=(True, "OK 5")):
                with patch("controllers.file_import_controller.threading") as mock_threading:
                    # Prevent actual thread from starting
                    mock_threading.Thread.return_value.start = MagicMock()
                    ctrl.import_file(path)
                    on_start.assert_called_once()
        finally:
            os.unlink(path)


class TestImportLeads(unittest.TestCase):
    """Tests para FileImportController.import_leads()."""

    def test_invalid_file_calls_on_error(self):
        on_error = MagicMock()
        ctrl = FileImportController(MagicMock(), on_error, MagicMock())
        ctrl.import_leads("/no/existe.csv")
        on_error.assert_called_once()


if __name__ == "__main__":
    unittest.main()
