# components/grafico_circular.py

import flet as ft
from theme import CARD_LIGHT, CARD_DARK, TEXT_LIGHT, TEXT_DARK


class GraficoCircularHover(ft.Container):
    def __init__(self, data_rows, theme_mode: ft.ThemeMode | str = ft.ThemeMode.LIGHT):
        """
        data_rows: lista de tuplas (product_type, total_vendido)
        theme_mode: ft.ThemeMode.LIGHT / DARK o "light"/"dark"
        """
        self._data_rows = data_rows
        self._theme_mode = theme_mode
        self._hover_text = ft.Text("", size=12)

        super().__init__(
            content=self._build_chart(),
            padding=12,
            bgcolor=ft.Colors.SURFACE,
            border_radius=8,
            expand=True,
        )

    # -----------------------
    # Helpers de tema
    # -----------------------
    def _is_dark(self) -> bool:
        tm = self._theme_mode
        if isinstance(tm, ft.ThemeMode):
            return tm == ft.ThemeMode.DARK
        # por si viene como string
        return str(tm).lower() == "dark"

    def _current_card_color(self):
        return CARD_DARK if self._is_dark() else CARD_LIGHT

    def _current_text_color(self):
        return TEXT_DARK if self._is_dark() else TEXT_LIGHT

    def _get_palette(self):
        # paleta de sectores según tema
        if self._is_dark():
            return [
                ft.Colors.CYAN,
                ft.Colors.AMBER,
                ft.Colors.LIME,
                ft.Colors.PINK,
                ft.Colors.ORANGE,
                ft.Colors.INDIGO,
                ft.Colors.TEAL,
            ]
        else:
            return [
                ft.Colors.BLUE,
                ft.Colors.RED,
                ft.Colors.GREEN,
                ft.Colors.PURPLE,
                ft.Colors.ORANGE,
                ft.Colors.BROWN,
                ft.Colors.TEAL,
            ]

    # -----------------------
    # Construcción del chart
    # -----------------------
    def _build_chart(self):
        if not self._data_rows:
            return ft.Text("⚠ No hay datos para graficar.", size=16, color=self._current_text_color())

        labels = [str(r[0]) for r in self._data_rows]
        values = []
        
        for r in self._data_rows:
            try:
                # Intenta convertir el segundo valor a float
                val = float(r[1]) if isinstance(r[1], (int, float)) else float(str(r[1]).replace(",", "."))
                values.append(val)
            except (ValueError, TypeError):
                print(f"⚠ No se puede convertir '{r[1]}' a número, usando 0")
                values.append(0.0)
        
        total = sum(values)
        if total <= 0:
            return ft.Text("⚠ Datos inválidos.", size=16, color=self._current_text_color())

        palette = self._get_palette()
        text_color = self._current_text_color()

        # sectores
        sections = []
        for idx, (label, val) in enumerate(zip(labels, values)):
            pct = val / total * 100
            sections.append(
                ft.PieChartSection(
                    value=val,
                    title=f"{label}\n{pct:.1f}%",
                    title_style=ft.TextStyle(
                        size=10,
                        color=ft.Colors.WHITE,
                        weight=ft.FontWeight.BOLD,
                    ),
                    color=palette[idx % len(palette)],
                )
            )

        pie_chart = ft.PieChart(
            sections=sections,
            sections_space=2,
            center_space_radius=50,
            expand=True,
        )

        # leyenda
        legend_rows = []
        for idx, (label, val) in enumerate(zip(labels, values)):
            pct = val / total * 100
            color = palette[idx % len(palette)]
            legend_rows.append(
                ft.Row(
                    [
                        ft.Container(width=16, height=16, bgcolor=color, border_radius=4),
                        ft.Text(label, size=12, color=text_color, expand=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(f"{val:.2f} €", size=12, weight=ft.FontWeight.W_600, color=text_color),
                        ft.Text(f"{pct:.1f}%", size=12, weight=ft.FontWeight.W_600, color=text_color, width=50),
                    ],
                    spacing=8,
                )
            )

        return ft.Row(
            [
                ft.Column(
                    [
                        ft.Text(
                            "🍰 Distribución de ventas",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=text_color,
                        ),
                        pie_chart,
                        self._hover_text,
                    ],
                    spacing=10,
                    expand=True,
                ),
                ft.Column(
                    [
                        ft.Text("Detalle", size=14, weight=ft.FontWeight.BOLD, color=text_color),
                        ft.Column(legend_rows, spacing=8, expand=True),
                    ],
                    spacing=10,
                    expand=True,
                ),
            ],
            spacing=20,
            expand=True,
        )

    # -----------------------
    # API para reaccionar al cambio de tema
    # -----------------------
    def set_theme_mode(self, theme_mode: ft.ThemeMode | str):
        """Llamar cuando cambie page.theme_mode."""
        self._theme_mode = theme_mode
        self.bgcolor = ft.Colors.SURFACE,
        self.content = self._build_chart()
        self.update()
