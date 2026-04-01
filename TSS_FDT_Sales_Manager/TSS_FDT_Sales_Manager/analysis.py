import sqlite3
import polars as pl
from db import DB_NAME
from datetime import datetime, date


DB_NAME = "sales.db"


def get_db_connection():
    """Obtiene conexión a la base de datos SQLite."""
    return sqlite3.connect(DB_NAME)


def get_sales_summary(start_date=None, end_date=None):
    """
    Obtiene resumen de ventas agrupado por tipo de producto.
    Retorna tuplas: (product_type, total_vendido)
    """
    try:
        conn = get_db_connection()
        
        # Query: agrupar por product_type y sumar price
        query = """
        SELECT 
            product_type, 
            SUM(CAST(price AS REAL)) as total
        FROM sales
        """
        
        # Agregar filtros de fecha si existen
        if start_date or end_date:
            filters = []
            if start_date:
                filters.append(f"date >= '{start_date}'")
            if end_date:
                filters.append(f"date <= '{end_date}'")
            query += " WHERE " + " AND ".join(filters)
        
        query += " GROUP BY product_type ORDER BY total DESC"
        
        df = pl.read_database(query, conn)
        conn.close()
        
    except Exception as e:
        print(f"Error leyendo datos: {e}")
        return None, None

    if df.is_empty():
        print("⚠ No hay datos disponibles")
        return None, None

    # Calcular promedio
    try:
        promedio = df.select(pl.col("total")).mean().item()
    except Exception:
        promedio = 0

    return df, promedio


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
