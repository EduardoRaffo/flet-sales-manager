# components/mostrar_grafico.py

import flet as ft
import inspect
from typing import Optional


class GraficoVentas(ft.Container):

    def __init__(self, rows, width: int = 900, height: int = 400):

        super().__init__(padding=12, expand=True)

        if not rows:

            self.content = ft.Text("⚠ No hay datos para graficar.", size=16)

            return

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

        # Crear los grupos de barras intentando adaptarnos a la API disponible
        def _find_class(*names) -> Optional[type]:
            for n in names:
                c = getattr(ft, n, None)
                if c is not None:
                    return c
            return None

        group_cls = _find_class("BarChartGroup")
        rod_cls = _find_class("BarChartRod", "BarChartBar", "Bar")

        def _make_rod(value):
            if not rod_cls:
                return None
            sig = None
            try:
                sig = inspect.signature(rod_cls)
            except Exception:
                sig = None
            # posibles nombres de parámetro para la altura/valor
            value_names = ["to_y", "toY", "to", "value", "y", "height"]
            color_names = ["color", "bgcolor", "background_color"]
            kwargs = {}
            for vn in value_names:
                if sig is None or vn in sig.parameters:
                    kwargs[vn] = value
                    break
            for cn in color_names:
                if sig is None or cn in sig.parameters:
                    kwargs[cn] = ft.Colors.BLUE
                    break
            try:
                return rod_cls(**kwargs) if kwargs else rod_cls(value)
            except Exception:
                # último recurso: instanciar con posición
                try:
                    return rod_cls(value)
                except Exception:
                    return None

        bar_groups = []
        if group_cls and rod_cls:
            # elegir el nombre correcto para los elementos del grupo
            try:
                group_sig = inspect.signature(group_cls)
                group_param_candidates = ["rods", "bars", "items", "values"]
                group_param = None
                for cand in group_param_candidates:
                    if cand in group_sig.parameters:
                        group_param = cand
                        break
            except Exception:
                group_param = "rods"

            for i, value in enumerate(values):
                rod = _make_rod(value)
                if rod is None:
                    bar_groups = []
                    break
                if group_param:
                    bar_groups.append(group_cls(x=i, **{group_param: [rod]}))
                else:
                    # intento por posición
                    try:
                        bar_groups.append(group_cls(i, [rod]))
                    except Exception:
                        bar_groups = []
                        break

        # Si no pudimos construir bar_groups con la API del chart, usaremos fallback
        if bar_groups:
            chart = ft.BarChart(
                bar_groups=bar_groups,
                border=ft.border.all(
                    1, ft.Colors.with_opacity(0.2, ft.Colors.ON_SURFACE)
                ),
                left_axis=ft.ChartAxis(
                    labels_size=40,
                    title=ft.Text("€ vendidos", size=14),
                ),
                bottom_axis=ft.ChartAxis(
                    labels=[
                        ft.ChartAxisLabel(value=i, label=ft.Text(labels[i]))
                        for i in range(len(labels))
                    ],
                    labels_size=60,
                    title=ft.Text("Productos", size=14),
                ),
                tooltip_bgcolor=ft.Colors.with_opacity(
                    0.9, ft.Colors.PRIMARY_CONTAINER
                ),
                max_y=max_y,
                interactive=True,
                animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
                expand=True,
            )
        else:
            # Fallback: dibujar barras simples si la versión de Flet no soporta BarChartGroup/BarChartRod
            bars_ui = []
            for label, v in zip(labels, values):
                pct = (v / max_y) if max_y else 0
                bars_ui.append(
                    ft.Column(
                        [
                            ft.Row([ft.Text(label, width=220), ft.Text(f"{v:.2f} €")]),
                            ft.Container(
                                height=18,
                                width=700,
                                bgcolor=ft.Colors.GREY_200,
                                border_radius=8,
                                content=ft.Container(
                                    width=int(700 * pct),
                                    bgcolor=ft.Colors.BLUE,
                                    border_radius=8,
                                ),
                            ),
                        ],
                        spacing=6,
                    )
                )

            chart = ft.Column(bars_ui, spacing=10, expand=True)

        self.content = ft.Column(
            [
                ft.Text("📊 Ventas por producto", size=20, weight=ft.FontWeight.BOLD),
                chart,
            ],
            spacing=20,
            expand=True,
        )
