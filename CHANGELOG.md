# Changelog

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).

---

## [Sin versionar] — 2026-03-25

### Corregido
- **`components/tabla_resumen.py`** — Añadido método público `update_theme(theme_mode)` (R9 fix)
  - `TablaResumen` carecía de este método; `VentasView.update_theme()` lo invocaba con `hasattr()` pero nunca ejecutaba la mutación de colores.
  - Al cambiar entre modo claro/oscuro, el color de cabecera de la tabla (`heading_row_color`) no se actualizaba.
  - La implementación solo muta `heading_row_color`; no llama `self.update()` — el orquestador (`VentasView`) es responsable de `page.update()` (R7 conforme).
  - El método privado `_apply_theme()` se mantiene intacto para uso interno en `did_mount()`.

### Añadido
- `core/SCHEMA.md` — schema explícito de `sales.db` (tablas, columnas, tipos, FK)
- Sección "Getting Started" en `README.md` para onboarding de desarrolladores
- Nota de precedencia en `docs/technical/01_architecture.md`

### Eliminado
- `docs/technical/02_contracts.md` — legacy Flet 0.28.x, ya obsoleto
- `docs/technical/AUDIT_*.md` / `CLOSURE_*.md` / `DECISION_*.md` / `SUMMARY_*.md` — auditorías y decisiones históricas ya incorporadas en AGENTS.md
- `docs/archive/` completo — documentación no-normativa de fases pasadas; el historial vive en Git

---

## [Sin versionar] — 2026-03-24

### Añadido
- Documentación completa del esquema de base de datos (`docs/technical/07_database_schema.md`)
- `CHANGELOG.md` para trazabilidad de versiones
- `CONTRIBUTING.md` con guía para contribuidores
- Catálogo de componentes (`docs/technical/component_catalog.md`)
- Contratos de services y controllers (`docs/technical/service_contracts.md`)
- Función `clear_table()` centralizada en `core/db.py` con whitelist de tablas
- Docstrings Google-style uniformes en archivos Python

### Eliminado
- `analysis/time_series_utils.py` — stub incompleto, duplicado por `time_grouping.py`
- `analysis/funnel_analysis.py` — código muerto nunca invocado
- Imports muertos: `Dict` en `evolution_analysis.py`, `datetime` en `html_sections.py` y `html_template.py`

---

## [2.1.1] — 2026-03-22

### Cambiado
- Actualización de `CLAUDE.md` a v1.2.0
- Actualización de `AGENTS.md` a v2.1.1
- Flet actualizado a 0.82.0 + flet-charts 0.82.0 + flet-desktop 0.82.0

---

## [2.1.0] — 2026-02-03

### Añadido
- Índice maestro de documentación técnica (`docs/technical/00_INDEX.md`)
- Documentación de módulos sellada (`docs/technical/03_modules.md`)
- Flujos operativos: NORMAL, COMPARE, EXPORT (`docs/technical/04_flows.md`)
- 6 ADRs en `docs/technical/06_architectural_decisions.md`
- Manual de usuario completo (11 secciones en `docs/user_manual/`)

---

## [2.0.0] — 2026-01-25

### Cambiado
- **BREAKING:** Nuevo contrato de theme para Flet 0.80.5+ (reglas R1–R9)
- Contratos legacy C-01..C-03 marcados como OBSOLETOS
- `AGENTS.md` establecido como fuente única de verdad (reemplaza `docs/technical/02_contracts.md`)

### Añadido
- `theme/THEME_AGENTS.md` — contrato definitivo del sistema de tema
- Cláusula anti-heurística R9 para `update_theme()`
- Inyección R9 en todos los componentes
- Auditoría formal de contratos completada y sellada

---

## [1.0.0] — 2025 (versión inicial)

### Añadido
- Aplicación FDT CRM Desktop con Flet
- Arquitectura de 10 capas
- Módulos: dashboard, ventas, clientes, leads
- Importación Excel/CSV (`core/importer.py`)
- Análisis con Polars: ventas, clientes, evolución, marketing
- Reportes HTML embebidos con Matplotlib
- Base de datos SQLite con 6 tablas
- Sistema de tema claro/oscuro

---

*Este changelog se reconstruyó a partir de los contratos técnicos vigentes.*
