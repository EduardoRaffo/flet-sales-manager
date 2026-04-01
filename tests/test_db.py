"""
Tests para core/db.py — Conexión SQLite, esquema y migraciones.
"""

import unittest
import sqlite3
from unittest.mock import patch, MagicMock
from pathlib import Path
from tests.conftest import create_test_db, seed_clients, seed_sales, NonClosingConnection


class TestGetBasePath(unittest.TestCase):
    """Tests para get_base_path()."""

    def test_returns_path_from_source(self):
        from core.db import get_base_path
        result = get_base_path()
        self.assertIsInstance(result, Path)
        self.assertTrue(result.exists())

    @patch("core.db.sys")
    def test_returns_exe_parent_when_frozen(self, mock_sys):
        mock_sys.frozen = True
        mock_sys.executable = "/fake/path/app.exe"
        from core.db import get_base_path
        result = get_base_path()
        self.assertEqual(result, Path("/fake/path"))


class TestGetConnection(unittest.TestCase):
    """Tests para get_connection()."""

    @patch("core.db.DB_NAME", ":memory:")
    @patch("core.db.DATA_PATH")
    def test_connection_returns_sqlite3(self, mock_path):
        mock_path.mkdir = MagicMock()
        from core.db import get_connection
        conn = get_connection()
        self.assertIsInstance(conn, sqlite3.Connection)
        conn.close()

    @patch("core.db.DB_NAME", ":memory:")
    @patch("core.db.DATA_PATH")
    def test_connection_enables_foreign_keys(self, mock_path):
        mock_path.mkdir = MagicMock()
        from core.db import get_connection
        conn = get_connection()
        result = conn.execute("PRAGMA foreign_keys").fetchone()
        self.assertEqual(result[0], 1)
        conn.close()


class TestInitDb(unittest.TestCase):
    """Tests para init_db() usando BD in-memory."""

    def setUp(self):
        raw = sqlite3.connect(":memory:")
        raw.execute("PRAGMA foreign_keys=ON;")
        self.conn = NonClosingConnection(raw)

    def tearDown(self):
        self.conn.real_close()

    @patch("core.db.get_connection")
    def test_creates_all_tables(self, mock_conn):
        mock_conn.return_value = self.conn
        from core.db import init_db
        init_db()
        cursor = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = {row[0] for row in cursor.fetchall()}
        expected = {"clients", "sales", "leads", "marketing_spend", "import_metadata", "funnel_events"}
        self.assertTrue(expected.issubset(tables), f"Missing tables: {expected - tables}")

    @patch("core.db.get_connection")
    def test_idempotent_double_init(self, mock_conn):
        mock_conn.return_value = self.conn
        from core.db import init_db
        init_db()
        init_db()  # No debe lanzar excepción

    @patch("core.db.get_connection")
    def test_creates_indices(self, mock_conn):
        mock_conn.return_value = self.conn
        from core.db import init_db
        init_db()
        cursor = self.conn.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indices = {row[0] for row in cursor.fetchall()}
        self.assertIn("idx_sales_date", indices)
        self.assertIn("idx_leads_source", indices)
        self.assertIn("idx_spend_source", indices)


class TestClearTable(unittest.TestCase):
    """Tests para clear_table() y aliases."""

    def setUp(self):
        self.conn = create_test_db()
        seed_clients(self.conn)
        seed_sales(self.conn)

    def tearDown(self):
        self.conn.real_close()

    @patch("core.db.get_connection")
    def test_clear_allowed_table_succeeds(self, mock_conn):
        mock_conn.return_value = self.conn
        from core.db import clear_table
        result = clear_table("sales")
        self.assertTrue(result)
        count = self.conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
        self.assertEqual(count, 0)

    @patch("core.db.get_connection")
    def test_clear_disallowed_table_returns_false(self, mock_conn):
        from core.db import clear_table
        result = clear_table("sqlite_master")
        self.assertFalse(result)

    @patch("core.db.get_connection")
    def test_clear_unknown_table_returns_false(self, mock_conn):
        from core.db import clear_table
        result = clear_table("nonexistent_table")
        self.assertFalse(result)

    @patch("core.db.get_connection")
    def test_clear_sales_table_alias(self, mock_conn):
        mock_conn.return_value = self.conn
        from core.db import clear_sales_table
        result = clear_sales_table()
        self.assertTrue(result)

    @patch("core.db.get_connection")
    def test_clear_clients_table_alias(self, mock_conn):
        mock_conn.return_value = self.conn
        # Primero limpiar sales (FK cascade)
        self.conn.execute("DELETE FROM sales")
        self.conn.commit()
        from core.db import clear_clients_table
        result = clear_clients_table()
        self.assertTrue(result)

    @patch("core.db.get_connection")
    def test_clear_leads_table_alias(self, mock_conn):
        mock_conn.return_value = self.conn
        from core.db import clear_leads_table
        result = clear_leads_table()
        self.assertTrue(result)


class TestEnsureLeadsTable(unittest.TestCase):
    """Tests para ensure_leads_table()."""

    @patch("core.db.get_connection")
    def test_creates_leads_table_if_missing(self, mock_conn):
        raw = sqlite3.connect(":memory:")
        raw.execute("PRAGMA foreign_keys=ON;")
        raw.execute("""
            CREATE TABLE clients(id TEXT PRIMARY KEY, name TEXT NOT NULL,
            cif TEXT NOT NULL, address TEXT, contact_person TEXT, email TEXT)
        """)
        raw.commit()
        conn = NonClosingConnection(raw)
        mock_conn.return_value = conn

        from core.db import ensure_leads_table
        ensure_leads_table()

        tables = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
        self.assertIn("leads", tables)
        conn.real_close()

    @patch("core.db.get_connection")
    def test_idempotent_when_already_exists(self, mock_conn):
        conn = create_test_db()
        mock_conn.return_value = conn

        from core.db import ensure_leads_table
        ensure_leads_table()
        ensure_leads_table()  # No debe lanzar excepción
        conn.real_close()


if __name__ == "__main__":
    unittest.main()
