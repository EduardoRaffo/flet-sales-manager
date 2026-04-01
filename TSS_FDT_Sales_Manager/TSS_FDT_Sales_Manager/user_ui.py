import flet as ft
from views.dashboard_view import DashboardView
from views.ventas_view import VentasView
from views.clientes_view import ClientesView
from theme import build_darkmode_button


class FDTApp(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True, spacing=0)
        self.page = page
        
        # Crear las vistas una sola vez
        self.dashboard_view = None
        self.ventas_view = None
        self.clientes_view = None

        # Tabs principales
        self.tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="Dashboard"),
                ft.Tab(text="Ventas"),
                ft.Tab(text="Clientes"),
            ],
            on_change=self._on_tab_change,
        )

        # Botón de dark mode
        self.dark_btn = build_darkmode_button(page)

        # Barra superior: tabs + botón alineados (compacta)
        self.top_bar = ft.Row(
            [
                self.tabs,
                ft.Container(self.dark_btn),
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Contenedor para la vista activa
        self.content_container = ft.Container(expand=True)

        self.controls = [
            self.top_bar,
            self.content_container,
        ]

        # Cargar la vista inicial
        self._load_view(0)

    def _on_tab_change(self, e):
        self._load_view(e.control.selected_index)

    def _load_view(self, index: int):
        if index == 0:
            if not self.dashboard_view:
                self.dashboard_view = DashboardView(
                    self.page,
                    open_file_picker=self._open_file_picker,
                    go_to_ventas=lambda: self._go_to_tab(1),
                    go_to_clientes=lambda: self._go_to_tab(2),
                )
            view = self.dashboard_view
        elif index == 1:
            if not self.ventas_view:
                self.ventas_view = VentasView(self.page)
            view = self.ventas_view
        elif index == 2:
            if not self.clientes_view:
                self.clientes_view = ClientesView(self.page)
            view = self.clientes_view
        else:
            view = ft.Column([ft.Text("Vista no disponible")], expand=True)

        self.content_container.content = view
        self.page.update()

    def _open_file_picker(self):
        """Abre el file picker desde dashboard."""
        self._go_to_tab(1)
        if self.ventas_view and self.ventas_view.upload_picker:
            # Abrimos el file picker directamente
            self.ventas_view.upload_picker.pick_files(allow_multiple=False)

    def _go_to_tab(self, tab_index: int):
        """Cambia a un tab específico."""
        self.tabs.selected_index = tab_index
        self._load_view(tab_index)
