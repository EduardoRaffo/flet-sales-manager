import os
import flet as ft

from importer import import_csv_to_db
from analysis import get_sales_summary
from components.resumen_card import ResumenCard
from components.tabla_resumen import TablaResumen


class VentasView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True, spacing=20)
        self.page = page

        self.output = ft.Text(size=14)
        self.summary_container = ft.Container()

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
                ],
                spacing=10,
            ),
            self.summary_container,
            self.output,
        ]

    def open_file_picker(self):
        self.upload_picker.pick_files(allow_multiple=False)

    # 📥 Importación de CSV/Excel
    def handle_file(self, e: ft.FilePickerResultEvent):
        if not e.files:
            self.output.value = "❌ No se seleccionó ningún archivo."
            self.page.update()
            return

        file = e.files[0]
        file_path = file.path

        if not os.path.exists(file_path):
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
            self.summary_container.content = None
            self.output.value = "⚠ No hay datos cargados."
            self.page.update()
            return

        rows = df.rows()

        tabla = TablaResumen(rows)
        card = ResumenCard(promedio)

        self.summary_container.content = ft.Column([tabla, card], spacing=20)
        self.page.update()
