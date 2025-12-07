import os
import flet as ft


class DashboardView(ft.Column):
    def __init__(self, page, open_file_picker, go_to_ventas, go_to_clientes):
        super().__init__(expand=True)
        self.page = page

        self.open_file_picker = open_file_picker
        self.go_to_ventas = go_to_ventas
        self.go_to_clientes = go_to_clientes

        # Cuando cambiemos el tema, reconstruimos el dashboard
        self.page.on_theme_changed = lambda _: self.build_ui()

        self.build_ui()

    # -----------------------------------------------------
    #   COLORES REACTIVOS A MODO CLARO / OSCURO
    # -----------------------------------------------------
    def _get_colors(self):
        if self.page.theme_mode == ft.ThemeMode.DARK:
            return {
                "bg_card": ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_900),
                "icon": ft.Colors.CYAN_200,
                "text": ft.Colors.WHITE,
                "subtitle": ft.Colors.GREY_400,
            }
        else:
            return {
                "bg_card": ft.Colors.BLUE_50,
                "icon": ft.Colors.BLUE,
                "text": ft.Colors.BLACK,
                "subtitle": ft.Colors.GREY_700,
            }

    # -----------------------------------------------------
    #                  CONSTRUIR UI
    # -----------------------------------------------------
    def build_ui(self):
        # Limpiamos controles anteriores para reconstruir según el tema
        self.controls.clear()

        colors = self._get_colors()

        # Header sin botón de tema
        header_row = ft.Row(
            controls=[
                ft.Text(
                    "📊 Panel Principal",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=colors["text"],
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
        )

        subtitle = ft.Text(
            "Accede rápidamente a las funciones principales del sistema.",
            size=16,
            color=colors["subtitle"],
        )

        # Estilo base de las tarjetas
        card_style = dict(
            padding=20,
            width=300,
            bgcolor=colors["bg_card"],
            border_radius=16,
            ink=True,
            animate=ft.Animation(250, ft.AnimationCurve.EASE_OUT),
        )

        # --- Tarjeta Importar Ventas ---
        tarjeta_importar = ft.Container(
            **card_style,
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.FILE_UPLOAD, size=40, color=colors["icon"]),
                    ft.Text(
                        "Importar datos de ventas",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=colors["text"],
                    ),
                    ft.Text(
                        "Arrastra un archivo CSV aquí o haz clic para seleccionar.",
                        size=14,
                        color=colors["subtitle"],
                    ),
                ],
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            on_click=lambda _: self.open_file_picker(),  # ← AGREGAR self.
            on_hover=self._on_tarjeta_hover,
        )

        # Drag and drop handlers
        def on_drag_over(e):
            e.control.bgcolor = ft.Colors.with_opacity(0.3, colors["icon"])
            e.control.update()

        def on_drag_leave(e):
            e.control.bgcolor = colors["bg_card"]
            e.control.update()

        def on_drop(e):
            e.control.bgcolor = colors["bg_card"]
            e.control.update()
            
            # En Flet desktop, el archivo viene en e.data como ruta
            if e.data:
                file_path = e.data.strip()
                self._handle_dropped_file(file_path)

        tarjeta_importar.on_drag_over = on_drag_over
        tarjeta_importar.on_drag_leave = on_drag_leave
        tarjeta_importar.on_drop = on_drop

        # --- Tarjeta Resumen ---
        tarjeta_resumen = ft.Container(
            **card_style,
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.ANALYTICS, size=40, color=colors["icon"]),
                    ft.Text(
                        "Ver análisis de ventas",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=colors["text"],
                    ),
                    ft.Text(
                        "Mostrar los datos procesados recientemente.",
                        size=14,
                        color=colors["subtitle"],
                    ),
                ],
                spacing=10,
            ),
            on_click=lambda _: self.go_to_ventas(),
        )

        # --- Tarjeta Clientes ---
        tarjeta_clientes = ft.Container(
            **card_style,
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.GROUP, size=40, color=colors["icon"]),
                    ft.Text(
                        "Gestionar clientes",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=colors["text"],
                    ),
                    ft.Text(
                        "Añadir, editar o eliminar clientes.",
                        size=14,
                        color=colors["subtitle"],
                    ),
                ],
                spacing=10,
            ),
            on_click=lambda _: self.go_to_clientes(),
        )

        # ---- DISEÑO FINAL ----
        self.controls = [
            header_row,
            subtitle,
            ft.Container(height=20),
            ft.Row(
                controls=[
                    tarjeta_importar,
                    tarjeta_resumen,
                    tarjeta_clientes,
                ],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
            ),
        ]

    def _on_tarjeta_hover(self, e):
        """Efecto hover en las tarjetas."""
        if e.data == "true":
            e.control.scale = 1.05
        else:
            e.control.scale = 1.0
        e.control.update()

    def _handle_dropped_file(self, file_path):
        """Procesa el archivo arrastrado."""
        import os
        from importer import import_csv_to_db
        
        if not file_path or not os.path.exists(file_path):
            print(f"❌ Archivo no válido: {file_path}")
            return

        # Validar que sea CSV o Excel
        if not (file_path.endswith('.csv') or file_path.endswith('.xlsx')):
            print(f"❌ Solo se aceptan archivos CSV o XLSX")
            return

        ok, msg = import_csv_to_db(file_path)
        
        if ok:
            print(f"✅ {msg}")
        else:
            print(f"❌ {msg}")
