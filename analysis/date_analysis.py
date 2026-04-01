"""
Funciones de análisis y helpers de fechas.
"""

from .db_utils import get_db_connection
import polars as pl

def get_date_range():
    """Obtiene el rango de fechas disponibles en los datos."""
    try:
        conn = get_db_connection()
        query = "SELECT MIN(date) as min_date, MAX(date) as max_date FROM sales"
        df = pl.read_database(query, conn)
        conn.close()

        if df.is_empty():
            return None, None

        min_date = df.select(pl.col("min_date")).item()
        max_date = df.select(pl.col("max_date")).item()

        return min_date, max_date
    except Exception as e:
        print(f"Error obteniendo rango de fechas: {e}")
        return None, None
