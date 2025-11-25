import flet as ft

class DashboardView(ft.Column):
    def __init__(self, page, open_file_picker, go_to_ventas, go_to_clientes):
        super().__init__(expand=True)
        self.page = page

        self.open_file_picker = open_file_picker
        self.go_to_ventas = go_to_ventas
        self.go_to_clientes = go_to_clientes

        self.build_ui()

    def build_ui(self):
        title = ft.Text(
            "📊 Panel Principal",
            size=28,
            weight=ft.FontWeight.BOLD,
        )

        subtitle = ft.Text(
            "Accede rápidamente a las funciones principales del sistema.",
            size=16,
            color=ft.Colors.GREY_700,
        )

        card_style = dict(
            padding=20,
            width=300,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=12,
            ink=True,
        )

        # ---------- Tarjetas ----------
        tarjeta_importar = ft.Container(
            **card_style,
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.FILE_UPLOAD, size=40, color=ft.Colors.BLUE),
                    ft.Text("Importar datos de ventas", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Sube archivos CSV o Excel para analizarlos.", size=14),
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.START,
            ),
            on_click=lambda _: self.open_file_picker(),
        )

        tarjeta_resumen = ft.Container(
            **card_style,
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.ANALYTICS, size=40, color=ft.Colors.BLUE),
                    ft.Text("Ver análisis de ventas", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Mostrar los datos procesados recientemente.", size=14),
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.START,
            ),
            on_click=lambda _: self.go_to_ventas(),
        )

        tarjeta_clientes = ft.Container(
            **card_style,
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.GROUP, size=40, color=ft.Colors.BLUE),
                    ft.Text("Gestionar clientes", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Añadir, editar o eliminar clientes.", size=14),
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.START,
            ),
            on_click=lambda _: self.go_to_clientes(),
        )

        self.controls = [
            title,
            subtitle,
            ft.Container(height=20),
            ft.Row(
                controls=[tarjeta_importar, tarjeta_resumen, tarjeta_clientes],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
            )
        ]
