import sqlite3
import polars as pl
from db import DB_NAME


def get_sales_summary():
    """
    Devuelve:
    - resumen: Polars DataFrame con total vendido por tipo de producto
    - promedio: precio medio (ticket medio por venta)
    """

    conn = sqlite3.connect(DB_NAME)

    try:
        df = pl.read_database("SELECT * FROM sales", conn)
    finally:
        conn.close()

    if df.is_empty():
        return None, None

    # ----------------------------------------------------------
    # Convertir date a tipo fecha (si existe la columna "date")
    # ----------------------------------------------------------
    if "date" in df.columns:
        try:
            df = df.with_columns(pl.col("date").str.strptime(pl.Date, strict=False))
        except Exception:
            # Si algún valor no se puede convertir, se ignora
            pass

    # ----------------------------------------------------------
    # Resumen: total vendido por tipo de producto
    # ----------------------------------------------------------
    resumen = (
        df.group_by("product_type")
        .agg(pl.sum("price").alias("total_vendido"))
        .sort("product_type")
    )

    # ----------------------------------------------------------
    # Promedio general de ventas (ticket medio por venta)
    # ----------------------------------------------------------
    promedio = df["price"].mean()

    return resumen, promedio
