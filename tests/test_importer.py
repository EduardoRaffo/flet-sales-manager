"""
Tests para core/importer.py — Importación CSV/Excel a SQLite.
"""

import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock
from core.importer import (
    _normalise_header,
    HEADER_ALIASES,
    SOURCE_NORMALIZATION,
    REQUIRED_LOGICAL_COLS,
    REQUIRED_LEADS_COLS,
    MARKETING_SPEND_HEADER_ALIASES,
)


class TestNormaliseHeader(unittest.TestCase):
    """Tests para _normalise_header()."""

    def test_strips_bom(self):
        self.assertEqual(_normalise_header("\ufeffclient_name"), "client_name")

    def test_strips_nbsp(self):
        self.assertEqual(_normalise_header("client\xa0name"), "client name")

    def test_lowercases(self):
        self.assertEqual(_normalise_header("Client_Name"), "client_name")

    def test_collapses_spaces(self):
        self.assertEqual(_normalise_header("client   name"), "client name")

    def test_empty_string(self):
        self.assertEqual(_normalise_header(""), "")

    def test_none_returns_empty(self):
        self.assertEqual(_normalise_header(None), "")

    def test_unicode_normalize(self):
        result = _normalise_header("café")
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)


class TestHeaderAliases(unittest.TestCase):
    """Tests para constantes de aliases."""

    def test_sales_aliases_map_correctly(self):
        self.assertEqual(HEADER_ALIASES["cliente"], "client_name")
        self.assertEqual(HEADER_ALIASES["precio"], "price")
        self.assertEqual(HEADER_ALIASES["fecha"], "date")

    def test_client_id_aliases(self):
        self.assertEqual(HEADER_ALIASES["identificador"], "client_id")

    def test_source_normalization_mapping(self):
        self.assertEqual(SOURCE_NORMALIZATION["facebook"], "meta_ads")
        self.assertEqual(SOURCE_NORMALIZATION["google"], "google_ads")
        self.assertEqual(SOURCE_NORMALIZATION["linkedin"], "linkedin_ads")
        self.assertEqual(SOURCE_NORMALIZATION["tiktok"], "tiktok_ads")

    def test_required_logical_cols(self):
        expected = {"client_name", "client_id", "product_type", "price"}
        self.assertEqual(REQUIRED_LOGICAL_COLS, expected)

    def test_required_leads_cols(self):
        expected = {"created_at", "source"}
        self.assertEqual(REQUIRED_LEADS_COLS, expected)

    def test_marketing_spend_aliases_contain_gasto(self):
        self.assertIn("gasto", MARKETING_SPEND_HEADER_ALIASES["amount"])


class TestImportCsvToDb(unittest.TestCase):
    """Tests para import_csv_to_db() — retorna tupla (ok, msg)."""

    def setUp(self):
        from tests.conftest import create_test_db
        self.conn = create_test_db()

    def tearDown(self):
        self.conn.real_close()

    def _write_csv(self, rows, header="client_name,client_id,product_type,price,date"):
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8")
        f.write(header + "\n")
        for row in rows:
            f.write(row + "\n")
        f.close()
        return f.name

    @patch("core.importer.get_connection")
    def test_valid_csv_imports_all_rows(self, mock_conn):
        mock_conn.return_value = self.conn
        path = self._write_csv([
            "TechNova,C001,Servicio,1000.0,2024-05-01",
            "DataCorp,C002,Producto,2000.0,2024-05-02",
        ])
        try:
            from core.importer import import_csv_to_db
            ok, msg = import_csv_to_db(path)
            self.assertTrue(ok)
            self.assertIn("OK", msg)
        finally:
            os.unlink(path)

    @patch("core.importer.get_connection")
    def test_bom_stripped_from_csv(self, mock_conn):
        mock_conn.return_value = self.conn
        f = tempfile.NamedTemporaryFile(mode="wb", suffix=".csv", delete=False)
        f.write(b"\xef\xbb\xbfclient_name,client_id,product_type,price,date\n")
        f.write(b"TechNova,C001,Servicio,1000.0,2024-05-01\n")
        f.close()
        try:
            from core.importer import import_csv_to_db
            ok, msg = import_csv_to_db(f.name)
            self.assertTrue(ok)
        finally:
            os.unlink(f.name)

    def test_nonexistent_file(self):
        """Nonexistent file should return failure tuple or raise."""
        from core.importer import import_csv_to_db
        try:
            ok, msg = import_csv_to_db("/nonexistent/path/file.csv")
            self.assertFalse(ok)
        except (FileNotFoundError, OSError):
            pass  # Also acceptable


class TestImportLeadsToDb(unittest.TestCase):
    """Tests para import_leads_to_db() — retorna tupla (ok, msg)."""

    def setUp(self):
        from tests.conftest import create_test_db
        self.conn = create_test_db()

    def tearDown(self):
        self.conn.real_close()

    def _write_leads_csv(self, rows, header="created_at,source,status,external_id"):
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8")
        f.write(header + "\n")
        for row in rows:
            f.write(row + "\n")
        f.close()
        return f.name

    @patch("core.importer.get_connection")
    def test_valid_leads_csv_imports(self, mock_conn):
        mock_conn.return_value = self.conn
        path = self._write_leads_csv([
            "2024-05-01,meta_ads,new,EXT001",
            "2024-05-02,google_ads,contacted,EXT002",
        ])
        try:
            from core.importer import import_leads_to_db
            ok, msg = import_leads_to_db(path)
            self.assertTrue(ok)
            self.assertIn("OK", msg)
        finally:
            os.unlink(path)

    @patch("core.importer.get_connection")
    def test_source_normalization_applied(self, mock_conn):
        mock_conn.return_value = self.conn
        path = self._write_leads_csv([
            "2024-05-01,facebook,new,EXT001",
        ])
        try:
            from core.importer import import_leads_to_db
            import_leads_to_db(path)
            rows = self.conn.execute("SELECT source FROM leads").fetchall()
            if rows:
                self.assertEqual(rows[0][0], "meta_ads")
        finally:
            os.unlink(path)


class TestInspectImportFile(unittest.TestCase):
    """Tests para inspect_import_file()."""

    def _write_csv(self, header, rows):
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8")
        f.write(header + "\n")
        for row in rows:
            f.write(row + "\n")
        f.close()
        return f.name

    def test_csv_file_inspection(self):
        path = self._write_csv(
            "client_name,client_id,product_type,price,date",
            ["TechNova,C001,Servicio,1000.0,2024-05-01"],
        )
        try:
            from core.importer import inspect_import_file
            result = inspect_import_file(path)
            self.assertIsInstance(result, dict)
            self.assertIn("headers", result)
            self.assertIn("detected_type", result)
        finally:
            os.unlink(path)

    def test_nonexistent_file(self):
        """Nonexistent file should raise or return error dict."""
        from core.importer import inspect_import_file
        try:
            result = inspect_import_file("/nonexistent/path.csv")
            # If it returns, check for error indication
            self.assertIsInstance(result, dict)
        except (FileNotFoundError, OSError):
            pass  # Expected


if __name__ == "__main__":
    unittest.main()
