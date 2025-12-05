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
                        "Sube archivos CSV o Excel para analizarlos.",
                        size=14,
                        color=colors["subtitle"],
                    ),
                ],
                spacing=10,
            ),
            on_click=lambda _: self.open_file_picker(),
        )

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
