# Schema de Base de Datos — sales.db

**Motor:** SQLite 3 | **Archivo:** `sales.db` (raíz del proyecto)

---

## Tablas

### `clients`
Catálogo de clientes. Clave primaria: `id` (UUID texto, generado en `core/db.py`).

| Columna | Tipo | NOT NULL | Descripción |
|---------|------|----------|-------------|
| `id` | TEXT | ✅ PK | UUID del cliente |
| `name` | TEXT | ✅ | Nombre comercial |
| `cif` | TEXT | ✅ | CIF / NIF |
| `address` | TEXT | — | Dirección postal |
| `contact_person` | TEXT | — | Persona de contacto |
| `email` | TEXT | — | Email de contacto |

---

### `sales`
Registro de ventas. Clave primaria: `id` (INTEGER AUTOINCREMENT).

| Columna | Tipo | NOT NULL | Descripción |
|---------|------|----------|-------------|
| `id` | INTEGER | ✅ PK | ID autoincremental |
| `client_name` | TEXT | ✅ | Nombre del cliente (desnormalizado) |
| `client_id` | TEXT | ✅ | FK → `clients.id` |
| `product_type` | TEXT | ✅ | Tipo de producto/servicio |
| `price` | REAL | ✅ | Importe de la venta |
| `date` | TEXT | ✅ | Fecha en formato `YYYY-MM-DD` |

**FK:** `client_id` → `clients.id` ON DELETE CASCADE

> `client_name` está desnormalizado intencionalmente para preservar el nombre histórico
> aunque el cliente sea renombrado posteriormente.

---

### `import_metadata`
Historial de importaciones de ficheros Excel/CSV.

| Columna | Tipo | NOT NULL | Descripción |
|---------|------|----------|-------------|
| `id` | INTEGER | ✅ PK | ID autoincremental |
| `imported_at` | TEXT | ✅ | Timestamp ISO 8601 de la importación |
| `file_name` | TEXT | — | Nombre del archivo importado |
| `total_rows` | INTEGER | — | Filas totales procesadas |
| `valid_rows` | INTEGER | — | Filas importadas correctamente |
| `rejected_rows` | INTEGER | — | Filas rechazadas por validación |
| `duration_seconds` | REAL | — | Duración de la importación en segundos |

---

## Diagrama de relaciones

```
clients (id PK)
    └── sales (client_id FK → clients.id  ON DELETE CASCADE)
```

`import_metadata` no tiene relaciones con otras tablas.

---

## Notas de implementación

- La BD se inicializa en `core/db.py` → función `init_db()`
- Las queries de análisis usan `core/db_utils.py` como capa de acceso
- Formato de fecha en `sales.date`: siempre `YYYY-MM-DD` (string, no DATE nativo)
- Los UUID de `clients.id` se generan con `uuid.uuid4()` en el importer
