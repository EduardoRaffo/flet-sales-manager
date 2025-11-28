import os
from importer import import_csv_to_db
from analysis import get_sales_summary
from components.resumen_card import ResumenCard
from components.tabla_resumen import TablaResumen
from components.mostrar_grafico import GraficoVentas
import flet as ft


class VentasView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True, spacing=20)
        self.page = page

        self.output = ft.Text(size=14)
        self.summary_container = ft.Container(
            expand=True,
            content=ft.Column(
                [ft.Text("📊 Carga datos para ver el resumen", size=16, color=ft.Colors.GREY)],
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        self.chart_container = ft.Container(
            expand=True,
            content=ft.Column(
                [ft.Text("📈 Carga datos para ver el gráfico", size=16, color=ft.Colors.GREY)],
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        self.main_row = ft.Row(
            [
                self.summary_container,
                self.chart_container,
            ],
            spacing=20,
            expand=True,
            wrap=False,
        )

        self.upload_picker = ft.FilePicker(on_result=self.handle_file)
        page.overlay.append(self.upload_picker)

        self.controls = [
            ft.Text("📈 Analizador de ventas", size=24, weight="bold"),
            ft.Row(
                [
                    ft.ElevatedButton(
                        "Importar archivo",
                        icon=ft.Icons.FILE_UPLOAD,
                        on_click=lambda _: self.upload_picker.pick_files(
                            allow_multiple=False
                        ),
                    ),
                    ft.ElevatedButton(
                        "Mostrar resumen",
                        icon=ft.Icons.SHOW_CHART,
                        on_click=self.show_summary,
                    ),
                    ft.ElevatedButton(
                        "Ver gráfico",
                        icon=ft.Icons.INSERT_CHART,
                        on_click=self.show_chart,
                    ),
                ],
                spacing=10,
            ),
            self.main_row,
            self.output,
        ]

    def open_file_picker(self):
        """Método utilizable desde el dashboard para abrir el selector."""
        self.upload_picker.pick_files(allow_multiple=False)

    # 📥 Importación de CSV/Excel
    def handle_file(self, e: ft.FilePickerResultEvent):
        if not e.files:
            self.output.value = "❌ No se seleccionó ningún archivo."
            self.page.update()
            return

        file = e.files[0]
        file_path = file.path

        if not file_path or not os.path.exists(file_path):
            self.output.value = "❌ Error leyendo el archivo."
            self.page.update()
            return

        success, msg = import_csv_to_db(file_path)
        self.output.value = f"✅ {msg}" if success else f"❌ {msg}"
        self.page.update()

    # 📊 Mostrar resumen
    def show_summary(self, e=None):
        try:
            df, promedio = get_sales_summary()
        except Exception as ex:
            self.output.value = f"❌ Error: {ex}"
            self.page.update()
            return

        if df is None:
            self.output.value = "⚠ No hay datos cargados."
            self.page.update()
            return

        rows = df.rows()
        tabla = TablaResumen(rows)
        card = ResumenCard(promedio)

        self.summary_container.content = ft.Column(
            [tabla, card],
            spacing=10,
            expand=True,  # ← IMPORTANTE
        )
        self.page.update()

    # 📈 Mostrar gráfico
    def show_chart(self, e=None):
        try:
            df, promedio = get_sales_summary()
        except Exception as ex:
            self.output.value = f"❌ Error: {ex}"
            self.page.update()
            return

        if df is None:
            self.chart_container.content = ft.Text("⚠ No hay datos cargados.")
            self.output.value = "⚠ No hay datos cargados."
            self.page.update()
            return

        rows = df.rows()
        grafico = GraficoVentas(rows)

        self.chart_container.content = grafico
        self.page.update()
