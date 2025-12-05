import os
import datetime
import flet as ft

from importer import import_csv_to_db
from analysis import get_sales_summary, get_date_range
from date_range import quick_range, month_range, year_range, normalize_iso, validate_range
from theme import clear_filter_button_style, date_filter_chip
from components.resumen_card import ResumenCard
from components.tabla_resumen import TablaResumen
from components.mostrar_grafico import GraficoVentas
from components.grafico_circular import GraficoCircularHover


class VentasView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True, spacing=20)
        self.page = page

        self.output = ft.Text(size=14)

        # Fecha seleccionada por el usuario (ISO 'YYYY-MM-DD' o None)
        self.start_date: str | None = None
        self.end_date: str | None = None

        # ============================================================
        #       FILTROS DE FECHA
        # ============================================================

        min_date, max_date = get_date_range()

        self.dp_start = ft.DatePicker(
            on_change=lambda e: self._on_date_change("start", e.control.value)
        )
        self.dp_end = ft.DatePicker(
            on_change=lambda e: self._on_date_change("end", e.control.value)
        )

        page.overlay.append(self.dp_start)
        page.overlay.append(self.dp_end)

        self.btn_pick_start = ft.ElevatedButton(
            "Elegir inicio",
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=self._open_start_picker,
        )

        self.lbl_start = date_filter_chip("Inicio: –", self.page.theme_mode == ft.ThemeMode.DARK)

        self.btn_pick_end = ft.ElevatedButton(
            "Elegir fin",
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=self._open_end_picker,
        )

        self.lbl_end = date_filter_chip("Fin: –", self.page.theme_mode == ft.ThemeMode.DARK)

        self.btn_apply_filter = ft.ElevatedButton(
            "Aplicar filtro",
            icon=ft.Icons.FILTER_LIST,
            on_click=self.apply_filter,
        )

        self.btn_clear_filters = ft.TextButton(
            "Limpiar filtros",
            icon=ft.Icons.CLEAR,
            on_click=self.clear_filters,
            style=clear_filter_button_style()
        )

        self.quick_buttons = ft.Row(
            [
                ft.ElevatedButton("Últimos 7 días", on_click=lambda _: self._quick_range(7)),
                ft.ElevatedButton("Últimos 30 días", on_click=lambda _: self._quick_range(30)),
                ft.ElevatedButton("Este mes", on_click=lambda _: self._quick_month()),
                ft.ElevatedButton("Este año", on_click=lambda _: self._quick_year()),
            ],
            spacing=10,
            wrap=True,
        )

        # Estado del filtro (expandido/contraído)
        self.filter_expanded = True

        self.btn_toggle_filter = ft.IconButton(
            icon=ft.Icons.EXPAND_LESS,
            tooltip="Contraer filtros",
            on_click=self._toggle_filter,
        )

        # Contenedor que se muestra/oculta
        self.filter_content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Column(
                            [ft.Text("Inicio", size=12), self.btn_pick_start, self.lbl_start],
                            spacing=5,
                            expand=1,
                        ),
                        ft.Column(
                            [ft.Text("Fin", size=12), self.btn_pick_end, self.lbl_end],
                            spacing=5,
                            expand=1,
                        ),
                    ],
                    spacing=10,
                    expand=True,
                ),
                ft.Row(
                    [
                        self.btn_apply_filter,
                        self.btn_clear_filters,
                    ],
                    spacing=10,
                ),
                ft.Text("Rangos rápidos", size=14, weight=ft.FontWeight.BOLD),
                self.quick_buttons,
            ],
            spacing=15,
            visible=True,
        )

        self.filter_card = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("🔎 Filtros de fecha", size=18, weight=ft.FontWeight.BOLD, expand=True),
                            self.btn_toggle_filter,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    self.filter_content,
                ],
                spacing=15,
            ),
            padding=15,
            border_radius=12,
            bgcolor=self._get_filter_bgcolor(),
        )

        # ============================================================
        #       CONTENEDORES PRINCIPALES
        # ============================================================

        self.summary_container = ft.Container(expand=1)
        self.chart_container = ft.Container(expand=1)

        self.content_row = ft.Row(
            [self.summary_container, self.chart_container],
            spacing=20,
            expand=True,
        )

        # ============================================================
        #       LAYOUT FINAL
        # ============================================================

        self.controls = [
            ft.Text("📈 Analizador de ventas", size=24, weight="bold"),
            ft.Row(
                [
                    # FILTROS A LA IZQUIERDA (ANCHO LIMITADO)
                    ft.Column(
                        [
                            self.filter_card,  # ← SIN CONTENEDOR CON ALTURA FIJA
                            # Botones debajo de los filtros
                            ft.Row(
                                [
                                    ft.ElevatedButton(
                                        "Importar archivo",
                                        icon=ft.Icons.FILE_UPLOAD,
                                        on_click=lambda _: self.upload_picker.pick_files(allow_multiple=False),
                                    ),
                                    ft.ElevatedButton(
                                        "Mostrar resumen",
                                        icon=ft.Icons.SHOW_CHART,
                                        on_click=self.show_summary,
                                    ),
                                    ft.ElevatedButton(
                                        "Ver gráficos",
                                        icon=ft.Icons.INSERT_CHART,
                                        on_click=self.show_both,
                                    ),
                                ],
                                spacing=10,
                                wrap=True,
                            ),
                        ],
                        width=600,
                        spacing=15,
                    ),
                    # CONTENIDO A LA DERECHA (GRÁFICOS Y RESUMEN)
                    self.content_row,
                ],
                spacing=20,
                expand=True,
            ),
            self.output,
        ]

    # ============================================================
    #   MÉTODOS DE EVENTOS (ANTES DE OTROS MÉTODOS)
    # ============================================================

    def _toggle_filter(self, e):
        """Expande o contrae el filtro de fechas."""
        self.filter_expanded = not self.filter_expanded
        self.filter_content.visible = self.filter_expanded
        
        if self.filter_expanded:
            self.btn_toggle_filter.icon = ft.Icons.EXPAND_LESS
            self.btn_toggle_filter.tooltip = "Contraer filtros"
        else:
            self.btn_toggle_filter.icon = ft.Icons.EXPAND_MORE
            self.btn_toggle_filter.tooltip = "Expandir filtros"
        
        self.page.update()

    def _open_start_picker(self, e):
        self.dp_start.open = True
        self.page.update()

    def _open_end_picker(self, e):
        self.dp_end.open = True
        self.page.update()

    def apply_filter(self, e):
        """Aplica los filtros de fecha y muestra resultados."""
        df, promedio = get_sales_summary(
            start_date=self.start_date,
            end_date=self.end_date,
        )

        if df is None:
            self.summary_container.content = None
            self.chart_container.content = None
            self.output.value = "⚠ No hay datos en ese rango."
            self.page.update()
            return

        rows = df.rows()

        tabla = TablaResumen(rows)
        card = ResumenCard(promedio)
        self.summary_container.content = ft.Column([tabla, card], spacing=10)

        grafico_circular = GraficoCircularHover(rows, theme_mode=self.page.theme_mode)
        grafico_barras = GraficoVentas(rows)
        self.chart_container.content = ft.Column([grafico_circular, grafico_barras], spacing=20)

        self.output.value = f"✅ Filtro aplicado: {self.start_date or 'inicio'} a {self.end_date or 'fin'}"
        self.page.update()

    def clear_filters(self, e):
        self.start_date = None
        self.lbl_start.content.controls[1].value = "Inicio: –"
        self.lbl_start.update()
        
        self.end_date = None
        self.lbl_end.content.controls[1].value = "Fin: –"
        self.lbl_end.update()

        self.dp_start.value = None
        self.dp_end.value = None

        self.dp_start.update()
        self.dp_end.update()

        self.show_both()
        self.output.value = "Filtros eliminados"
        self.page.update()

    # ============================================================
    #   OTROS MÉTODOS
    # ============================================================

    def open_file_picker(self):
        self.upload_picker.pick_files(allow_multiple=False)

    def handle_file(self, e: ft.FilePickerResultEvent):
        if not e.files:
            self.output.value = "❌ No se seleccionó ningún archivo."
            self.page.update()
            return

        file = e.files[0].path

        if not file or not os.path.exists(file):
            self.output.value = "❌ Error leyendo el archivo."
            self.page.update()
            return

        ok, msg = import_csv_to_db(file)
        self.output.value = f"✅ {msg}" if ok else f"❌ {msg}"
        self.page.update()

    def show_summary(self, e=None):
        """Muestra solo el resumen de ventas."""
        try:
            df, promedio = get_sales_summary()
        except Exception as ex:
            self.output.value = f"❌ Error: {ex}"
            self.page.update()
            return

        if df is None:
            self.summary_container.content = None
            self.chart_container.content = None
            self.output.value = "⚠ No hay datos cargados."
            self.page.update()
            return

        rows = df.rows()

        tabla = TablaResumen(rows)
        card = ResumenCard(promedio)

        self.summary_container.content = ft.Column([tabla, card], spacing=10)
        self.chart_container.content = None
        self.page.update()

    def show_both(self, e=None):
        """Muestra resumen + gráficos lado a lado."""
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
        self.summary_container.content = ft.Column([tabla, card], spacing=10)

        grafico_circular = GraficoCircularHover(rows, theme_mode=self.page.theme_mode)
        grafico_barras = GraficoVentas(rows)
        self.chart_container.content = ft.Column([grafico_circular, grafico_barras], spacing=20)

        self.page.update()

    def _on_date_change(self, which, value):
        """Se llama cuando el usuario selecciona una fecha en el DatePicker."""
        iso_value = normalize_iso(value)
        text = value.strftime("%Y-%m-%d") if value else "–"

        if which == "start":
            self.start_date = iso_value
            self.lbl_start.content.controls[1].value = f"Inicio: {text}"
            self.lbl_start.update()

        elif which == "end":
            self.end_date = iso_value
            self.lbl_end.content.controls[1].value = f"Fin: {text}"
            self.lbl_end.update()

    def _quick_range(self, days):
        start_iso, end_iso = quick_range(days)

        self.start_date = start_iso
        self.lbl_start.content.controls[1].value = f"Inicio: {start_iso[:10]}"
        self.lbl_start.update()

        self.end_date = end_iso
        self.lbl_end.content.controls[1].value = f"Fin: {end_iso[:10]}"
        self.lbl_end.update()

        self.apply_filter(None)

    def _quick_month(self):
        start_iso, end_iso = month_range()

        self.start_date = start_iso
        self.lbl_start.content.controls[1].value = f"Inicio: {start_iso[:10]}"
        self.lbl_start.update()

        self.end_date = end_iso
        self.lbl_end.content.controls[1].value = f"Fin: {end_iso[:10]}"
        self.lbl_end.update()

        self.apply_filter(None)

    def _quick_year(self):
        start_iso, end_iso = year_range()

        self.start_date = start_iso
        self.lbl_start.content.controls[1].value = f"Inicio: {start_iso[:10]}"
        self.lbl_start.update()

        self.end_date = end_iso
        self.lbl_end.content.controls[1].value = f"Fin: {end_iso[:10]}"
        self.lbl_end.update()

        self.apply_filter(None)

    def _get_filter_bgcolor(self):
        """Retorna color de fondo según el tema actual."""
        if self.page.theme_mode == ft.ThemeMode.DARK:
            return ft.Colors.with_opacity(0.15, ft.Colors.BLUE_300)
        else:
            return ft.Colors.with_opacity(0.1, ft.Colors.BLUE_600)
