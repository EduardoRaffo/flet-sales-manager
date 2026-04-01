"""Orquestador principal de la UI de FDT CRM Desktop.

Gestiona la navegación por pestañas (Dashboard, Ventas, Leads, Clientes),
el cambio de tema claro/oscuro y la propagación de update_theme() a todas
las vistas cacheadas.
"""

import flet as ft
import logging
from views.dashboard_view import DashboardView
from views.ventas_view import VentasView
from views.leads_view import LeadsView
from views.clientes_view import ClientesView
from utils.notifications import NotificationManager
from theme import get_icon_color

logger = logging.getLogger(__name__)

class FDTApp(ft.Column):
    """Aplicación principal. Contiene TabBar de navegación, body de contenido y botón de tema."""

    def __init__(self, page: ft.Page):
        super().__init__(expand=True, spacing=0)
        self._page = page  # Usar _page en lugar de page (page es property de solo lectura en Flet 0.80.5)
        # Cache de vistas (patrón correcto Flet 0.80.x)
        self._dashboard_view = None
        self._ventas_view = None
        self._leads_view = None
        self._clientes_view = None

        # ==============================
        # Export state (FilePicker ya no es global - se crea cuando se necesita)
        # ==============================
        self._pending_export_snapshot = None
        
        # Inicializar gestor de notificaciones
        self.notifications = NotificationManager(page)
        page.notifications = self.notifications
        self.logo_image = ft.Image(src="assets/fdt_logo.png",width=36,height=36,fit="contain")

        # Logo (a la izquierda del menú)
        self.logo = ft.Container(
            width=52,
            height=52,
            padding=8,
            border_radius=14,
            bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.SURFACE),
            content=self.logo_image,
        )

        def _tab_content(label: str, icon: str) -> ft.Control:
            icon_control = ft.Icon(icon, size=20)
            text_control = ft.Text(label, size=14, weight=ft.FontWeight.W_500)

            def _on_hover(e):
                # Resaltar icono y título al hacer hover
                if str(e.data).lower() == "true":
                    hover_color = get_icon_color(self._page.theme_mode)
                    icon_control.color = hover_color
                    text_control.color = hover_color
                else:
                    # Volver a colores por defecto del tema
                    icon_control.color = None
                    text_control.color = None
                e.control.update()

            return ft.Container(
                padding=ft.Padding.symmetric(horizontal=16, vertical=8),
                content=ft.Row(
                    [
                        icon_control,
                        text_control,
                    ],
                    spacing=8,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                on_hover=_on_hover,
            )

        # Navegación (Flet 0.80.5 — Tabs con TabBar)
        self.tab_bar = ft.TabBar(
            tabs=[
                ft.Tab(label=_tab_content("Dashboard", ft.Icons.DASHBOARD)),
                ft.Tab(label=_tab_content("Ventas", ft.Icons.TRENDING_UP)),
                ft.Tab(label=_tab_content("Leads", ft.Icons.PERSON_ADD)),
                ft.Tab(label=_tab_content("Clientes", ft.Icons.GROUP)),
            ],
            scrollable=False,
        )
        
        self.tabs = ft.Tabs(
            content=self.tab_bar,
            length=4,
            selected_index=0,
            on_change=self._on_tab_change,
            expand=True,  # Expande a todo el ancho disponible
        )

        # Botón de tema
        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip="Cambiar tema",
            on_click=self._toggle_theme,
        )

        # Contenedor de contenido
        self.body = ft.Container(
            expand=True,
            padding=ft.padding.only(left=12, right=12, top=20, bottom=0),
        )

        # Layout principal
        self.controls = [
            ft.Container(
                padding=ft.padding.symmetric(horizontal=12, vertical=12),
                content=ft.Row(
                    [
                        ft.Row([self.logo, self.tabs], spacing=14, expand=True),
                        self.theme_button,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ),
            self.body,
        ]

        # Cargar vista inicial
        self._load_view(0)
        
        # 🚀 FIX: Flag para debounce de cambios de tema
        self._theme_toggling = False

    def _on_tab_change(self, e):
        """Cambia de vista según la pestaña seleccionada."""
        idx = e.control.selected_index
        print(f"[TAB] CLICK EN PESTAÑA {idx}")
        old_view_type = type(self.body.content).__name__ if self.body.content else "None"
        print(f"[TAB] Saliendo de: {old_view_type}")
        self._load_view(idx)
        new_view_type = type(self.body.content).__name__ if self.body.content else "None"
        print(f"[TAB] Entrando a: {new_view_type}")
        print()

    def _load_view(self, index):
        """Carga (o reutiliza) la vista correspondiente al índice de pestaña."""
        if index == 0:
            if self._dashboard_view is None:
                self._dashboard_view = DashboardView(
                    self._page,
                    open_file_picker=self.request_import,
                    go_to_ventas=lambda: self._go_to_tab(1),
                    go_to_leads=lambda: self._go_to_tab(2),
                    go_to_clientes=lambda: self._go_to_tab(3),
                )
            self.body.content = self._dashboard_view
            print(f"[TAB] body.content ahora es {type(self.body.content).__name__} [ID: {id(self._dashboard_view)}]")
    
        elif index == 1:
            if self._ventas_view is None:
                self._ventas_view = VentasView(self._page)
                print(f"[TAB] VentasView CREADA [ID: {id(self._ventas_view)}]")
            else:
                print(f"[TAB] VentasView REUTILIZADA [ID: {id(self._ventas_view)}]")
            self.body.content = self._ventas_view
            print(f"[TAB] body.content ahora es {type(self.body.content).__name__} [ID: {id(self._ventas_view)}]")
    
        elif index == 2:
            if self._leads_view is None:
                self._leads_view = LeadsView(self._page)
                print(f"[TAB] LeadsView CREADA [ID: {id(self._leads_view)}]")
            else:
                print(f"[TAB] LeadsView REUTILIZADA [ID: {id(self._leads_view)}]")
            self.body.content = self._leads_view
            print(f"[TAB] body.content ahora es {type(self.body.content).__name__} [ID: {id(self._leads_view)}]")

        elif index == 3:
            if self._clientes_view is None:
                self._clientes_view = ClientesView(self._page)
                print(f"[TAB] ClientesView CREADA [ID: {id(self._clientes_view)}]")
            else:
                print(f"[TAB] ClientesView REUTILIZADA [ID: {id(self._clientes_view)}]")
            self.body.content = self._clientes_view
            print(f"[TAB] body.content ahora es {type(self.body.content).__name__} [ID: {id(self._clientes_view)}]")

        #self._page.update()


    def _go_to_tab(self, index):
        """Cambia a la pestaña especificada."""
        self.tabs.selected_index = index
        self._load_view(index)

    # =========================================================
    # API PÚBLICA — INTENCIONES DE IMPORT / EXPORT
    # =========================================================

    def request_import(self):
        """
        NO USADO - Dashboard maneja import directamente.
        Mantenido para compatibilidad con VentasView si es necesario.
        """
        pass

    def request_export(self, snapshot):
        """
        Intención: exportar datos desde Ventas.
        """
        self._pending_export_snapshot = snapshot
        self._page.run_task(lambda: self._export_file_async(snapshot))
    
    async def _export_file_async(self, snapshot):
        """Exporta el snapshot a HTML."""
        file_picker = ft.FilePicker()
        file_path = await file_picker.save_file(allowed_extensions=["html"])
        
        if not file_path:
            return
        
        # Delegar en VentasView
        vista = self.body.content
        if isinstance(vista, VentasView) and getattr(vista, "_mounted", False):
            vista.handle_export_file(file_path, snapshot)

    def _toggle_theme(self, e):
        """Alterna entre modo claro y oscuro (patrón oficial de Flet)."""
        if self._theme_toggling:
            return
        
        self._theme_toggling = True
        try:
            # Cambiar theme_mode directamente (patrón oficial)
            self._page.theme_mode = (
                ft.ThemeMode.DARK
                if self._page.theme_mode == ft.ThemeMode.LIGHT
                else ft.ThemeMode.LIGHT
            )
            
            # Actualizar icono del botón según el nuevo theme
            self.theme_button.icon = (
                ft.Icons.LIGHT_MODE
                if self._page.theme_mode == ft.ThemeMode.DARK
                else ft.Icons.DARK_MODE
            )
            
            # Actualizar logo según el nuevo theme
            self.logo_image.src = (
                "assets/fdt_logo_light.png"
                if self._page.theme_mode == ft.ThemeMode.DARK
                else "assets/fdt_logo.png"
            )
            
            self.logo.bgcolor = ft.Colors.with_opacity(
                0.08 if self._page.theme_mode == ft.ThemeMode.DARK else 0.04,
                ft.Colors.SURFACE
            )

            # Propagar theme a la vista activa (actualiza colores hardcoded)
            # Los colores semánticos (ON_SURFACE, SURFACE, etc.) se adaptan solos,
            # pero colores condicionales (GREEN_200/700, BLUE_200/700, etc.) requieren
            # update_theme() explícito en la vista.
            active_view = self.body.content
            if active_view is not None and hasattr(active_view, "update_theme"):
                active_view.update_theme()

            # Propagar actualización de tema a las vistas cacheadas (si existen)
            if self._dashboard_view and hasattr(self._dashboard_view, 'update_theme'):
                self._dashboard_view.update_theme()
            if self._ventas_view and hasattr(self._ventas_view, 'update_theme'):
                self._ventas_view.update_theme()
            if self._leads_view and hasattr(self._leads_view, 'update_theme'):
                self._leads_view.update_theme()
            if self._clientes_view and hasattr(self._clientes_view, 'update_theme'):
                self._clientes_view.update_theme()

            # page.update() final: envía todas las mutaciones al frontend
            self._page.update()
        finally:
            self._theme_toggling = False
