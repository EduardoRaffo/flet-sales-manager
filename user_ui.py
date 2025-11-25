import flet as ft
from views.ventas_view import VentasView
from views.dashboard_view import DashboardView
from views.clientes_view import ClientesView
from db import init_db


class FDTApp(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True)
        self.page = page

        init_db()

        # Crear vistas solo UNA vez
        self.ventas_view = VentasView(page)
        self.clientes_view = ClientesView(page)
        self.dashboard_view = DashboardView(
            page,
            open_file_picker=self.ventas_view.open_file_picker,
            go_to_ventas=lambda: self.go_to_tab(1),
            go_to_clientes=lambda: self.go_to_tab(2),
        )

        # Tabs principales
        self.tabs = ft.Tabs(
            selected_index=0,
            expand=True,
            tabs=[
                ft.Tab(text="Inicio", icon=ft.Icons.HOME, content=self.dashboard_view),
                ft.Tab("Ventas", icon=ft.Icons.SHOW_CHART, content=self.ventas_view),
                ft.Tab("Clientes", icon=ft.Icons.GROUP, content=self.clientes_view),
            ],
        )

        self.controls = [self.tabs]

    # Método para cambiar de tab
    def go_to_tab(self, index: int):
        self.tabs.selected_index = index
        self.page.update()
