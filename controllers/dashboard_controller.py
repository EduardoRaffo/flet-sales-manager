"""
Controlador de lógica para el Dashboard.
Separa la lógica de negocio de la UI.
"""
from core.db import clear_sales_table, clear_clients_table, clear_leads_table
from services.dashboard_kpi_service import DashboardKPIService
from domain.dashboard_kpi_snapshot import DashboardKPISnapshot


class DashboardController:
    """Controlador centralizado para operaciones del Dashboard."""

    @staticmethod
    def clear_sales():
        """
        Vacía la tabla de ventas.

        Returns:
            tuple: (success: bool, message: str)
        """
        if clear_sales_table():
            return True, "✔ Base de datos de ventas vaciada"
        return False, "Error al vaciar base de datos de ventas"

    @staticmethod
    def clear_clients():
        """
        Vacía la tabla de clientes.

        Returns:
            tuple: (success: bool, message: str)
        """
        if clear_clients_table():
            return True, "✔ Base de datos de clientes vaciada"
        return False, "Error al vaciar base de datos de clientes"

    @staticmethod
    def clear_leads():
        """
        Vacía la tabla de leads.

        Returns:
            tuple: (success: bool, message: str)
        """
        if clear_leads_table():
            return True, "✔ Base de datos de leads vaciada"
        return False, "Error al vaciar base de datos de leads"

    @staticmethod
    def get_dashboard_kpi_snapshot() -> DashboardKPISnapshot:
        """
        Obtiene el snapshot inmutable de KPIs del Dashboard (HOME).

        No lanza excepciones a la UI.
        """
        try:
            return DashboardKPIService.build_snapshot()
        except Exception:
            # Fallback defensivo: dashboard nunca debe romper
            return DashboardKPISnapshot.empty()
