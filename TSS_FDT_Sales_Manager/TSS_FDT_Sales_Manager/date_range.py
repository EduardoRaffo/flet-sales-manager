from datetime import date, datetime, timedelta
from typing import Optional, Tuple


# ============================================================
#   HELPERS DE FECHAS → SIEMPRE DEVUELVEN CADENAS ISO (YYYY-MM-DD)
# ============================================================

def _to_iso(d: date) -> str:
    """Convierte un objeto date a cadena ISO YYYY-MM-DD."""
    return d.strftime("%Y-%m-%d")


def quick_range(days: int, today: Optional[date] = None) -> Tuple[str, str]:
    """
    Devuelve (start_iso, end_iso) para los últimos `days` días, incluyendo hoy.
    Formato: 'YYYY-MM-DD'.
    """
    if today is None:
        today = date.today()
    start = today - timedelta(days=days)
    return _to_iso(start), _to_iso(today)


def month_range(today: Optional[date] = None) -> Tuple[str, str]:
    """
    Devuelve (start_iso, end_iso) para el mes actual hasta hoy.
    """
    if today is None:
        today = date.today()
    start = today.replace(day=1)
    return _to_iso(start), _to_iso(today)


def year_range(today: Optional[date] = None) -> Tuple[str, str]:
    """
    Devuelve (start_iso, end_iso) para el año actual hasta hoy.
    """
    if today is None:
        today = date.today()
    start = today.replace(month=1, day=1)
    return _to_iso(start), _to_iso(today)


# ============================================================
#   NORMALIZACIÓN ISO Y VALIDACIÓN
# ============================================================

def normalize_iso(value: Optional[object]) -> Optional[str]:
    """
    Normaliza cualquier representación de fecha a 'YYYY-MM-DD'.
    Acepta:
        - None → None
        - date / datetime → ISO
        - str en varios formatos comunes.
    Si no reconoce el formato, devuelve None (no lanza excepción).
    """
    if value is None:
        return None

    if isinstance(value, date) and not isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")

    if isinstance(value, datetime):
        return value.date().strftime("%Y-%m-%d")

    # Asumimos string u otro → lo convertimos a str
    s = str(value).strip()
    if not s:
        return None

    # Si ya parece ISO 'YYYY-MM-DD', lo dejamos tal cual
    if len(s) == 10 and s[4] == "-" and s[7] == "-":
        return s

    # Intentar parsear algunos formatos habituales (por si acaso)
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%Y.%m.%d"):
        try:
            dt = datetime.strptime(s, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Formato desconocido
    return None


def validate_range(
    start_iso: Optional[str],
    end_iso: Optional[str],
) -> Tuple[bool, Optional[str]]:
    """
    Valida que el rango (start_iso, end_iso) sea coherente.
    Las fechas deben venir ya en formato 'YYYY-MM-DD' o None.
    Devuelve:
        (True, None)  si es válido
        (False, "mensaje") si es inválido
    """
    if start_iso and end_iso and start_iso > end_iso:
        return False, "La fecha final no puede ser anterior a la fecha inicial."

    return True, None
