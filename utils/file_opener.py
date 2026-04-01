"""
Utilidad cross-platform para abrir archivos con la aplicación predeterminada.

Extrae el patrón duplicado os.startfile / subprocess.run(['open', ...])
que existía en ventas_view.py, leads_view.py y clientes_view.py.
"""

import os
import subprocess
import logging

logger = logging.getLogger(__name__)


def open_file_cross_platform(filepath: str) -> None:
    """
    Abre un archivo con la aplicación predeterminada del sistema operativo.

    - Windows: usa os.startfile()
    - macOS/Linux: fallback a subprocess.run(['open', filepath])
    - Si ambos fallan, registra un warning sin propagar la excepción.

    Args:
        filepath: Ruta absoluta del archivo a abrir.
    """
    try:
        os.startfile(filepath)  # Windows
    except (AttributeError, OSError):
        try:
            subprocess.run(['open', filepath])  # macOS
        except Exception:
            logger.warning(
                "No se pudo abrir automáticamente el archivo: %s", filepath
            )
