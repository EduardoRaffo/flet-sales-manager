import sqlite3
from db import DB_NAME


def add_client(name, cif, address, contact_person, email):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO clients (name, cif, address, contact_person, email)
        VALUES (?, ?, ?, ?, ?)
    """,
        (name, cif, address, contact_person, email),
    )
    conn.commit()
    conn.close()


def get_clients():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients")
    data = cursor.fetchall()
    conn.close()
    return data


def get_client_by_id(client_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    data = cursor.fetchone()
    conn.close()
    return data


def update_client(client_id, name, cif, address, contact_person, email):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE clients
        SET name=?, cif=?, address=?, contact_person=?, email=?
        WHERE id=?
    """,
        (name, cif, address, contact_person, email, client_id),
    )
    conn.commit()
    conn.close()


def delete_client(client_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
    conn.commit()
    conn.close()
