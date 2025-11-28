# components/mostrar_grafico.py

import flet as ft


class GraficoVentas(ft.Container):

    def __init__(self, rows):
        super().__init__(
            content=self._build_chart(rows),
            padding=12,
            bgcolor=ft.Colors.SURFACE,
            border_radius=8,
            expand=True,
        )

    def _build_chart(self, rows):
        if not rows:
            return ft.Text("⚠ No hay datos para graficar.", size=16)

        labels = [str(r[0]) for r in rows]

        try:
            values = [float(r[1]) for r in rows]
        except Exception:
            values = []
            for r in rows:
                try:
                    values.append(float(str(r[1]).replace(",", ".").strip()))
                except Exception:
                    values.append(0.0)

        max_y = max(values) * 1.2 if values else 1.0

        bars_ui = []
        for label, v in zip(labels, values):
            pct = (v / max_y) if max_y else 0
            bars_ui.append(
                ft.Column(
                    [
                        ft.Container(
                            height=int(250 * pct),  # ← AUMENTADO de 150 a 250
                            width=25,
                            bgcolor=ft.Colors.BLUE,
                            border_radius=8,
                            tooltip=f"{v:.2f} €",
                            alignment=ft.alignment.bottom_center,
                        ),
                        ft.Text(label, size=8, text_align=ft.TextAlign.CENTER),
                        ft.Text(f"{v:.2f} €", size=7, text_align=ft.TextAlign.CENTER),
                    ],
                    spacing=0,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.END,
                )
            )

        return ft.Column(
            [
                ft.Text("📊 Ventas por producto", size=16, weight=ft.FontWeight.BOLD),
                ft.Row(
                    bars_ui,
                    spacing=3,
                    vertical_alignment=ft.CrossAxisAlignment.END,
                    expand=True,
                ),
            ],
            spacing=10,
            expand=True,
        )
