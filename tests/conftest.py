"""
Fixtures compartidas para toda la suite de tests.

Provee:
- create_test_db(): Conexión SQLite :memory: con esquema completo
- Funciones seed_*() para insertar datos de prueba
- FIXED_DATE para tests deterministas
"""

import sqlite3
from datetime import date
from unittest.mock import patch
from functools import wraps

FIXED_DATE = date(2024, 5, 15)


class NonClosingConnection:
    """Wrapper around sqlite3.Connection that makes close() a no-op.

    Python 3.13 made Connection.close read-only, so we can't do
    conn.close = lambda: None. This proxy delegates everything to
    the real connection but ignores close() calls from production code.
    """

    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def close(self):
        """No-op — prevents production code from closing the test connection."""
        pass

    def real_close(self):
        """Actually close the underlying connection (call in tearDown)."""
        self._conn.close()

    def __getattr__(self, name):
        return getattr(self._conn, name)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass  # Don't close


def create_test_db() -> NonClosingConnection:
    """Crea una BD in-memory con el esquema completo del proyecto.

    Returns a NonClosingConnection wrapper so that production code calling
    conn.close() doesn't destroy the test DB mid-test.
    Use conn.real_close() in tearDown.
    """
    raw = sqlite3.connect(":memory:")
    raw.execute("PRAGMA foreign_keys=ON;")
    cursor = raw.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients(
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            cif TEXT NOT NULL,
            address TEXT,
            contact_person TEXT,
            email TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            client_id TEXT NOT NULL,
            product_type TEXT NOT NULL,
            price REAL NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads(
            id TEXT PRIMARY KEY,
            external_id TEXT,
            created_at TEXT NOT NULL,
            source TEXT NOT NULL,
            status TEXT NOT NULL,
            meeting_date TEXT,
            client_id TEXT,
            FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marketing_spend(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS import_metadata(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            imported_at TEXT NOT NULL,
            file_name TEXT,
            total_rows INTEGER,
            valid_rows INTEGER,
            rejected_rows INTEGER,
            duration_seconds REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS funnel_events(
            id TEXT PRIMARY KEY,
            client_id TEXT,
            lead_id TEXT,
            event_type TEXT NOT NULL,
            source TEXT,
            event_date TEXT NOT NULL,
            metadata TEXT,
            FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL,
            FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE SET NULL
        )
    """)

    # Indices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_client_name ON sales(client_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_product_type ON sales(product_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_client_id ON sales(client_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_client_id ON leads(client_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_source ON leads(source)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status)")

    raw.commit()
    return NonClosingConnection(raw)


def seed_clients(conn, rows=None):
    """Inserta clientes de prueba.

    rows: lista de tuplas (id, name, cif, address, contact_person, email)
    """
    if rows is None:
        rows = [
            ("C001", "TechNova", "A12345678", "Calle 1", "Juan", "juan@tech.com"),
            ("C002", "DataCorp", "B87654321", "Calle 2", "Ana", "ana@data.com"),
            ("C003", "CloudSoft", "C11223344", "Calle 3", "Pedro", "pedro@cloud.com"),
        ]
    conn.executemany(
        "INSERT INTO clients (id, name, cif, address, contact_person, email) VALUES (?,?,?,?,?,?)",
        rows,
    )
    conn.commit()


def seed_sales(conn, rows=None):
    """Inserta ventas de prueba.

    rows: lista de tuplas (client_name, client_id, product_type, price, date)
    """
    if rows is None:
        rows = [
            ("TechNova", "C001", "Servicio", 1000.0, "2024-05-01"),
            ("TechNova", "C001", "Producto", 2000.0, "2024-05-05"),
            ("DataCorp", "C002", "Servicio", 1500.0, "2024-05-10"),
            ("DataCorp", "C002", "Servicio", 500.0, "2024-04-15"),
            ("CloudSoft", "C003", "Producto", 3000.0, "2024-05-12"),
        ]
    conn.executemany(
        "INSERT INTO sales (client_name, client_id, product_type, price, date) VALUES (?,?,?,?,?)",
        rows,
    )
    conn.commit()


def seed_leads(conn, rows=None):
    """Inserta leads de prueba.

    rows: lista de tuplas (id, external_id, created_at, source, status, meeting_date, client_id)
    """
    if rows is None:
        rows = [
            ("L001", "EXT1", "2024-05-01", "meta_ads", "new", None, None),
            ("L002", "EXT2", "2024-05-03", "google_ads", "contacted", None, None),
            ("L003", "EXT3", "2024-05-05", "meta_ads", "meeting", "2024-05-10", None),
            ("L004", "EXT4", "2024-04-20", "linkedin_ads", "converted", "2024-04-25", "C001"),
            ("L005", "EXT5", "2024-05-08", "google_ads", "lost", None, None),
        ]
    conn.executemany(
        "INSERT INTO leads (id, external_id, created_at, source, status, meeting_date, client_id) VALUES (?,?,?,?,?,?,?)",
        rows,
    )
    conn.commit()


def seed_marketing_spend(conn, rows=None):
    """Inserta gasto de marketing de prueba.

    rows: lista de tuplas (source, amount, date)
    """
    if rows is None:
        rows = [
            ("meta_ads", 500.0, "2024-05-01"),
            ("google_ads", 300.0, "2024-05-01"),
            ("linkedin_ads", 200.0, "2024-04-15"),
        ]
    conn.executemany(
        "INSERT INTO marketing_spend (source, amount, date) VALUES (?,?,?)",
        rows,
    )
    conn.commit()


def patch_db(test_conn):
    """Decorator que parchea get_db_connection y get_connection para usar una conexión de test."""
    def decorator(func):
        @wraps(func)
        @patch("analysis.db_utils.get_db_connection", return_value=test_conn)
        @patch("core.db.get_connection", return_value=test_conn)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator
