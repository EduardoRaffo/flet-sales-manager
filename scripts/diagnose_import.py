#!/usr/bin/env python3
"""
Script de diagnóstico para verificar estado de la BD y proceso de importación.
"""
import sys
from pathlib import Path

# Agregar raíz del proyecto al path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from core.db import get_connection, DB_NAME

def main():
    print(f"🔍 DIAGNÓSTICO DE IMPORTACIÓN")
    print(f"=" * 60)
    print(f"Base de datos: {DB_NAME}")
    print()
    
    # 1. Verificar si DB existe
    db_path = Path(DB_NAME)
    if db_path.exists():
        print(f"✅ BD existe: {db_path}")
        print(f"   Tamaño: {db_path.stat().st_size} bytes")
    else:
        print(f"❌ BD NO existe: {db_path}")
        return
    
    print()
    
    # 2. Conectar y verificar tablas
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Verificar tablas
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' ORDER BY name
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"✅ Tablas encontradas:")
            for (table_name,) in tables:
                print(f"   - {table_name}")
        else:
            print(f"❌ NO hay tablas en la BD")
            conn.close()
            return
        
        print()
        
        # 3. Contar registros en cada tabla
        print(f"📊 REGISTROS POR TABLA:")
        for (table_name,) in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   {table_name}: {count} registros")
        
        print()
        
        # 4. Verificar últimas ventas
        cursor.execute("SELECT COUNT(*) FROM sales")
        sales_count = cursor.fetchone()[0]
        
        if sales_count > 0:
            print(f"✅ Ventas detectadas: {sales_count}")
            cursor.execute("""
                SELECT client_name, client_id, product_type, price, date
                FROM sales 
                ORDER BY date DESC 
                LIMIT 3
            """)
            print(f"   Últimas 3 ventas:")
            for row in cursor.fetchall():
                print(f"      {row}")
        else:
            print(f"⚠️  NO hay ventas en la BD")
        
        print()
        
        # 5. Verificar clientes
        cursor.execute("SELECT COUNT(*) FROM clients")
        clients_count = cursor.fetchone()[0]
        print(f"👥 Clientes: {clients_count}")
        
        if clients_count > 0:
            cursor.execute("""
                SELECT id, name FROM clients LIMIT 3
            """)
            print(f"   Primeros 3 clientes:")
            for client_id, name in cursor.fetchall():
                print(f"      {client_id}: {name}")
        
        print()
        
        # 6. Verificar metadata de importación
        cursor.execute("SELECT COUNT(*) FROM import_metadata")
        metadata_count = cursor.fetchone()[0]
        print(f"📋 Importaciones registradas: {metadata_count}")
        
        if metadata_count > 0:
            cursor.execute("""
                SELECT imported_at, file_name, total_rows, valid_rows, rejected_rows
                FROM import_metadata
                ORDER BY imported_at DESC
                LIMIT 3
            """)
            print(f"   Últimas 3 importaciones:")
            for row in cursor.fetchall():
                print(f"      {row}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error al conectar a BD: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
