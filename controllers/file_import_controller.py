"""Controlador de importación de archivos (ventas, leads, mixto).

Ejecuta importaciones en threads daemon y notifica resultado
mediante callbacks (on_success, on_error, on_start).
"""

import os
import re
import threading
from typing import Callable, Optional
from core.importer import import_csv_to_db, import_leads_to_db, import_marketing_spend_to_db, inspect_import_file


class FileImportController:
    """Controlador centralizado para la importación de archivos."""
    
    def __init__(self, on_success: Callable, on_error: Callable, on_start: Callable):
        """
        Inicializa el controlador.
        
        Args:
            on_success: Callback(message) cuando la importación es exitosa
            on_error: Callback(message) cuando hay un error
            on_start: Callback() cuando inicia la importación
        """
        self.on_success = on_success
        self.on_error = on_error
        self.on_start = on_start
    
    def validate_file(self, file_path: Optional[str]) -> tuple[bool, Optional[str]]:
        """
        Valida que el archivo exista y sea accesible.
        
        Retorna: (es_valido, mensaje_error_o_none)
        """
        if not file_path:
            return False, "No se seleccionó ningún archivo"
        
        if not os.path.exists(file_path):
            return False, "El archivo no existe o no es accesible"
        
        return True, None
    
    def import_file(self, file_path: str) -> None:
        """
        Importa un archivo en un hilo de fondo.
        
        Valida el archivo y ejecuta la importación de forma asincrónica.
        Dispara los callbacks correspondientes.
        """
        # Validar archivo
        is_valid, error_msg = self.validate_file(file_path)
        if not is_valid:
            self.on_error(error_msg)
            return
        
        # Notificar inicio
        self.on_start()
        
        # Ejecutar en segundo plano
        def process():
            try:
                ok, msg = import_csv_to_db(file_path)
                
                if ok:
                    self.on_success(msg)
                else:
                    self.on_error(msg)
            except Exception as e:
                self.on_error(f"Error durante la importación: {str(e)}")
        
        threading.Thread(target=process, daemon=True).start()

    def import_sales(self, file_path: str) -> None:
        """Alias explícito para importar ventas (delega a import_file)."""
        self.import_file(file_path)

    def import_leads(self, file_path: str) -> None:
        """Importa leads en un hilo de fondo."""
        is_valid, error_msg = self.validate_file(file_path)
        if not is_valid:
            self.on_error(error_msg)
            return

        self.on_start()

        def process():
            try:
                ok, msg = import_leads_to_db(file_path)
                if ok:
                    self.on_success(msg)
                else:
                    self.on_error(msg)
            except Exception as e:
                self.on_error(f"Error durante la importación de leads: {str(e)}")

        threading.Thread(target=process, daemon=True).start()

    def import_marketing_spend(self, file_path: str) -> None:
        """Importa marketing_spend en un hilo de fondo."""
        is_valid, error_msg = self.validate_file(file_path)
        if not is_valid:
            self.on_error(error_msg)
            return

        self.on_start()

        def process():
            try:
                ok, msg = import_marketing_spend_to_db(file_path)
                if ok:
                    self.on_success(msg)
                else:
                    self.on_error(msg)
            except Exception as e:
                self.on_error(f"Error durante la importación de inversión: {str(e)}")

        threading.Thread(target=process, daemon=True).start()

    def import_both(self, file_path: str) -> None:
        """Importa leads + ventas desde el mismo archivo (tipo mixed) en un solo hilo."""
        is_valid, error_msg = self.validate_file(file_path)
        if not is_valid:
            self.on_error(error_msg)
            return

        # Obtener el total de filas antes de lanzar el hilo (operación rápida, sin BD)
        try:
            total_rows = inspect_import_file(file_path).get("row_count", 0)
        except Exception:
            total_rows = None

        self.on_start()

        def _parse_count(msg: str) -> int:
            """Extrae el número de filas importadas del mensaje del importer."""
            m = re.search(r"OK (\d+)", msg)
            return int(m.group(1)) if m else 0

        def process():
            had_error = False
            lead_count = 0
            sale_count = 0
            error_parts = []

            try:
                ok_leads, msg_leads = import_leads_to_db(file_path)
                if ok_leads:
                    lead_count = _parse_count(msg_leads)
                else:
                    had_error = True
                    error_parts.append(f"Leads: {msg_leads}")
            except Exception as e:
                had_error = True
                error_parts.append(f"Error en leads: {str(e)}")

            try:
                ok_sales, msg_sales = import_csv_to_db(file_path)
                if ok_sales:
                    sale_count = _parse_count(msg_sales)
                else:
                    had_error = True
                    error_parts.append(f"Ventas: {msg_sales}")
            except Exception as e:
                had_error = True
                error_parts.append(f"Error en ventas: {str(e)}")

            if had_error:
                self.on_error(" | ".join(error_parts))
                return

            # Filas genuinamente inválidas = filas totales - leads importados - ventas importadas
            # (las "rechazadas esperadas" de cada importer son exactamente las filas del otro tipo)
            msg = f"{sale_count} ventas + {lead_count} leads importados correctamente."
            if total_rows is not None:
                genuine_invalid = total_rows - lead_count - sale_count
                if genuine_invalid > 0:
                    msg += f" ⚠ {genuine_invalid} filas inválidas ignoradas."

            self.on_success(msg)

        threading.Thread(target=process, daemon=True).start()
