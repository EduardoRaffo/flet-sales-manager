import sqlite3

DB_NAME = "sales.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Tabla de ventas
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sales(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            client_id TEXT NOT NULL,
            product_type TEXT NOT NULL,
            price REAL NOT NULL,
            date TEXT NOT NULL
        )
        """
    )

    # Tabla de clientes
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS clients(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            cif TEXT NOT NULL,
            address TEXT,
            contact_person TEXT,
            email TEXT
        )
        """
    )

    conn.commit()
    conn.close()
