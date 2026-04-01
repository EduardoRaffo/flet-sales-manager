"""
components/import_preview_dialog.py

Factory de componente UI: Import Preview Dialog.

Muestra un AlertDialog con:
  - Badge visual del tipo de archivo detectado (sales / leads / mixed)
  - Advertencia visual si el tipo es "mixed"
  - Estadísticas opcionales del archivo (filas totales, válidas, inválidas)
  - Lista de headers como chips en layout Wrap horizontal
  - Botones Cancelar / Importar archivo

NO ejecuta la importación directamente.
Delega la acción en los callbacks on_confirm / on_cancel provistos por el caller.

Uso:
    dialog = create_import_preview_dialog(
        page=page,
        detected_type="sales",
        headers=["fecha", "cliente", "precio", ...],
        on_confirm=lambda: controller.import_sales(file_path),
        on_cancel=lambda: None,
    )
    page.show_dialog(dialog)
"""

import flet as ft
from typing import Final

# ── Constantes ────────────────────────────────────────────────────────────────

_MAX_HEADERS_SHOWN: Final[int] = 10

# ── Tablas de tipos ───────────────────────────────────────────────────────────

_TYPE_LABELS = {
    "sales": "VENTAS",
    "leads": "LEADS",
    "mixed": "MIXTO (ventas + leads)",
    "marketing_spend": "INVERSIÓN MARKETING",
}

_TYPE_COLORS = {
    "sales":           ft.Colors.BLUE_700,
    "leads":           ft.Colors.GREEN_700,
    "mixed":           ft.Colors.PURPLE_700,
    "marketing_spend": ft.Colors.ORANGE_700,
}

_TYPE_ICONS = {
    "sales":           ft.Icons.PAYMENTS,
    "leads":           ft.Icons.PERSON_ADD,
    "mixed":           ft.Icons.COMPARE_ARROWS,
    "marketing_spend": ft.Icons.ATTACH_MONEY,
}


# ── Helpers internos ──────────────────────────────────────────────────────────

def _stat_minimal(label: str, value: int, color: str):
    """Minimal stat display: large number with small uppercase label."""
    return ft.Column(
        controls=[
            ft.Text(
                str(value),
                size=32,
                weight=ft.FontWeight.W_900,
                color=color,
            ),
            ft.Text(
                label.upper(),
                size=10,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.with_opacity(0.6, ft.Colors.ON_SURFACE_VARIANT),
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=-5,
        tight=True,
    )


def _short_header(text: str | None) -> str:
    """Shorten very long header names for chip labels."""
    if not text:
        return ""
    text = str(text)
    if len(text) <= 18:
        return text
    return text[:15] + "..."


# ── Factory ───────────────────────────────────────────────────────────────────

def create_import_preview_dialog(
    page,
    detected_type: str,
    headers: list[str],
    row_count: int | None = None,
    valid_rows: int | None = None,
    invalid_rows: int | None = None,
    on_confirm=None,
    on_cancel=None,
    preview_rows: list[dict] | None = None,  # TODO: mostrar tabla de preview (futuro)
) -> ft.AlertDialog:
    """
    Crea y devuelve un ft.AlertDialog de preview de importación.

    Parámetros:
        page          : ft.Page activa
        detected_type : "sales" | "leads" | "mixed"
        headers       : Lista de headers detectados en el archivo
        row_count     : Total de filas en el archivo (opcional)
        valid_rows    : Filas válidas detectadas (opcional)
        invalid_rows  : Filas inválidas detectadas (opcional)
        on_confirm    : Callable() invocado cuando el usuario confirma
        on_cancel     : Callable() invocado cuando el usuario cancela
        preview_rows  : Reservado para uso futuro (primeras filas del CSV)

    El dialog NO abre ni cierra otros dialogs.
    El caller abre el dialog con page.show_dialog(dialog).
    """
    # ── Normalizar inputs ─────────────────────────────────────────────────
    headers = list(headers) if headers else []

    type_label = _TYPE_LABELS.get(detected_type, detected_type.upper())
    type_color = _TYPE_COLORS.get(detected_type, ft.Colors.GREY_700)
    type_icon  = _TYPE_ICONS.get(detected_type, ft.Icons.UPLOAD_FILE)

    # ── Badge de tipo ─────────────────────────────────────────────────────
    type_badge = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(type_icon, color=type_color, size=16),
                ft.Text(
                    type_label,
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color=type_color,
                ),
            ],
            tight=True,
        ),
        bgcolor=ft.Colors.with_opacity(0.1, type_color),
        border=ft.border.all(1, ft.Colors.with_opacity(0.25, type_color)),
        padding=ft.padding.symmetric(horizontal=12, vertical=6),
        border_radius=8,
    )

    # ── Advertencia para archivos mixed ───────────────────────────────────
    mixed_warning = None
    if detected_type == "mixed":
        mixed_warning = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.WARNING_AMBER, color=ft.Colors.AMBER_700, size=16),
                    ft.Text(
                        "Este archivo contiene ventas y leads. Ambos tipos se importarán.",
                        size=12,
                        color=ft.Colors.AMBER_700,
                    ),
                ],
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.only(top=6),
        )

    # ── Estadísticas del archivo (sección condicional) ────────────────────
    stats_section = None
    if any(v is not None for v in (row_count, valid_rows, invalid_rows)):
        stat_controls = []
        if row_count is not None:
            stat_controls.append(_stat_minimal("Totales", row_count, ft.Colors.BLUE_600))
        if valid_rows is not None:
            if stat_controls:
                stat_controls.append(ft.VerticalDivider(width=1, color=ft.Colors.OUTLINE_VARIANT))
            stat_controls.append(_stat_minimal("Válidas", valid_rows, ft.Colors.GREEN_600))
        if invalid_rows is not None:
            if stat_controls:
                stat_controls.append(ft.VerticalDivider(width=1, color=ft.Colors.OUTLINE_VARIANT))
            color_invalid = ft.Colors.RED_400 if invalid_rows > 0 else ft.Colors.ON_SURFACE_VARIANT
            stat_controls.append(_stat_minimal("Inválidas", invalid_rows, color_invalid))

        summary_lines = []
        if valid_rows is not None:
            summary_lines.append(
                ft.Text(
                    f"Se importarán {valid_rows} filas válidas.",
                    size=12,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                )
            )
        if invalid_rows is not None and invalid_rows > 0:
            summary_lines.append(
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.WARNING_AMBER, color=ft.Colors.AMBER_700, size=14),
                        ft.Text(
                            f"{invalid_rows} filas no se importarán por errores.",
                            size=12,
                            color=ft.Colors.AMBER_700,
                        ),
                    ],
                    spacing=4,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )

        # Clean divisor-based stats without containers
        stats_section = ft.Container(
            padding=ft.padding.symmetric(vertical=25),
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=stat_controls,
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    *summary_lines,
                ],
                spacing=12,
                tight=True,
            ),
        )

    # ── Headers - Glassmorphism Style ────────────────────────────────────
    shown = headers[:_MAX_HEADERS_SHOWN]
    extra = max(0, len(headers) - _MAX_HEADERS_SHOWN)

    if shown:
        tag_controls = [
            ft.Container(
                content=ft.Text(
                    _short_header(h),
                    size=11,
                    weight=ft.FontWeight.W_500,
                    italic=True,
                    color=ft.Colors.with_opacity(0.75, ft.Colors.BLUE_700),
                ),
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=6,
            )
            for h in shown
        ]
        if extra > 0:
            tag_controls.append(
                ft.Container(
                    content=ft.Text(
                        f"... y {extra} más",
                        size=10,
                        italic=True,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                )
            )

        headers_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        f"ESTRUCTURA DEL ARCHIVO ({len(headers)} COLUMNAS)",
                        size=11,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_700,
                    ),
                    ft.Row(
                        controls=tag_controls,
                        wrap=True,
                        spacing=10,
                    ),
                ],
                spacing=20,
            ),
            padding=ft.padding.all(5),
        )
    else:
        headers_section = ft.Text(
            "No se detectaron columnas",
            size=13,
            italic=True,
            color=ft.Colors.ON_SURFACE_VARIANT,
        )

    # ── Contenido del dialog (jerarquía visual) ───────────────────────────
    content_controls = [
        ft.Text(
            "Tipo de archivo detectado:",
            size=13,
            weight=ft.FontWeight.W_600,
            color=ft.Colors.ON_SURFACE,
        ),
        type_badge,
    ]

    if mixed_warning:
        content_controls.append(mixed_warning)

    if stats_section:
        content_controls.append(stats_section)

    content_controls.append(headers_section)

    content = ft.Container(
        width=660,
        padding=ft.padding.only(top=8),
        bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.BLUE_600),
        content=ft.Column(
            controls=content_controls,
            spacing=20,
            tight=True,
        ),
    )

    # ── Handlers de botones ───────────────────────────────────────────────
    def handle_confirm(e):
        if not dialog.open:
            return  # Prevenir doble click
        dialog.open = False
        page.update()
        if on_confirm:
            on_confirm()

    def handle_cancel(e):
        if not dialog.open:
            return
        dialog.open = False
        page.update()
        if on_cancel:
            on_cancel()

    # ── Dialog ────────────────────────────────────────────────────────────
    dialog = ft.AlertDialog(
        shape=ft.RoundedRectangleBorder(radius=16),
        title=ft.Row(
            controls=[
                ft.Icon(type_icon, color=type_color, size=20),
                ft.Text(
                    "Vista previa de importación",
                    size=18,
                    weight=ft.FontWeight.W_600,
                ),
            ],
            spacing=10,
        ),
        content=content,
        content_padding=ft.padding.symmetric(horizontal=28, vertical=20),
        actions=[
            ft.TextButton("Cancelar", on_click=handle_cancel),
            ft.FilledButton(
                f"Importar {valid_rows} filas" if valid_rows is not None else "Importar archivo",
                icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                on_click=handle_confirm,
                disabled=valid_rows == 0 if valid_rows is not None else False,
                bgcolor=ft.Colors.BLUE_800,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    return dialog

