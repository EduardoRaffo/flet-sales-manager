"""
Script de benchmark manual para medir el rendimiento de queries y verificar índices en la base de datos.
No es un test unitario automático.
Ubicación recomendada: tests/
"""
import sqlite3
import time

DB_NAME = 'sales.db'

# Query típica de reporte (por producto y fecha)
query = '''
SELECT product_type, SUM(price) as total, COUNT(*) as cantidad
FROM sales
WHERE date >= '2025-01-01' AND date <= '2025-12-31'
GROUP BY product_type
'''

def timed_query():
    conn = sqlite3.connect(DB_NAME)
    start = time.time()
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    elapsed = time.time() - start
    conn.close()
    return elapsed, len(rows)

# Ejecutar varias veces para calentar caché
for _ in range(3):
    timed_query()

# Medir tiempo real
elapsed, n = timed_query()
print(f"Tiempo de consulta: {elapsed:.4f} s, filas: {n}")

# Mostrar índices existentes
conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()
cur.execute("PRAGMA index_list('sales')")
print('Índices en sales:')
for idx in cur.fetchall():
    print(idx)
conn.close()
