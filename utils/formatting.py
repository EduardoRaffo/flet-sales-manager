"""
Utilidades de formateo para presentación consistente de valores monetarios.

Proporciona funciones centralizadas para formatear moneda en formato europeo (€)
con período para miles y coma para decimales, garantizando consistencia entre
UI y exportación HTML.
"""


def format_eur(value: float, decimals: int = 2) -> str:
    """
    Formatea un valor numérico a formato europeo con símbolo € (€ X.XXX,XX).

    Args:
        value: Valor numérico a formatear
        decimals: Número de decimales (default 2)

    Returns:
        String formateado: "€ X.XXX,XX" o "€ X" si decimals=0

    Example:
        >>> format_eur(1234.56)
        '€ 1.234,56'
        >>> format_eur(1234567.89)
        '€ 1.234.567,89'
        >>> format_eur(1234, decimals=0)
        '€ 1.234'
    """
    try:
        # Usar formato US (coma para miles, punto para decimales)
        us_format = f"{float(value):,.{decimals}f}"
        # Convertir a formato europeo (punto para miles, coma para decimales)
        european_format = us_format.replace(",", "|").replace(".", ",").replace("|", ".")
        return f"€ {european_format}"
    except (ValueError, TypeError):
        return "€ 0,00"


def format_eur_no_symbol(value: float, decimals: int = 2) -> str:
    """
    Formatea un valor numérico a formato europeo SIN símbolo € (X.XXX,XX).

    Útil para renderizado HTML donde el símbolo está en CSS o contexto.

    Args:
        value: Valor numérico a formatear
        decimals: Número de decimales (default 2)

    Returns:
        String formateado: "X.XXX,XX" o "X" si decimals=0

    Example:
        >>> format_eur_no_symbol(1234.56)
        '1.234,56'
    """
    try:
        us_format = f"{float(value):,.{decimals}f}"
        return us_format.replace(",", "|").replace(".", ",").replace("|", ".")
    except (ValueError, TypeError):
        return "0,00"


def format_eur_signed(value: float, decimals: int = 2) -> str:
    """
    Formatea un valor numérico a formato europeo CON signo (+/-) (±X.XXX,XX).

    Útil para mostrar cambios en comparativas.

    Args:
        value: Valor numérico a formatear (puede ser negativo)
        decimals: Número de decimales (default 2)

    Returns:
        String formateado: "+X.XXX,XX" o "-X.XXX,XX"

    Example:
        >>> format_eur_signed(1234.56)
        '+1.234,56'
        >>> format_eur_signed(-1234.56)
        '-1.234,56'
    """
    try:
        sign = "+" if float(value) >= 0 else ""
        us_format = f"{float(value):,.{decimals}f}"
        european_format = us_format.replace(",", "|").replace(".", ",").replace("|", ".")
        return f"{sign}{european_format}".replace("+-", "-")
    except (ValueError, TypeError):
        return "+0,00"


def mask_sensitive(value: str) -> str:
    """
    Enmascara un valor sensible para mostrar en UI con patrón hover-reveal.

    Los valores vacíos y los placeholders ("—", "-") pasan sin cambios.
    Todos los demás se reemplazan por "••••••••" hasta que el usuario
    pase el cursor sobre el control (ver _make_masked_cell / _masked_info_row).

    Args:
        value: Valor a enmascarar (CIF, email, teléfono, persona de contacto…)

    Returns:
        "••••••••" o el valor original si está vacío / es placeholder.
    """
    if not value or str(value).strip() in ("—", "-", ""):
        return value
    return "••••••••"
