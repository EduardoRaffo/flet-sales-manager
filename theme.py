import flet as ft


# ============================================================
#   PALETA DE COLORES PRINCIPAL (marca FDT)
# ============================================================

PRIMARY_COLOR = ft.Colors.BLUE_600
PRIMARY_DARK = ft.Colors.BLUE_300

BACKGROUND_LIGHT = ft.Colors.GREY_50
BACKGROUND_DARK = ft.Colors.GREY_900

CARD_LIGHT = ft.Colors.WHITE
CARD_DARK = ft.Colors.GREY_800

TEXT_LIGHT = ft.Colors.BLACK
TEXT_DARK = ft.Colors.WHITE


# ============================================================
#   CONFIGURACIÓN DE TEMAS: CLARO + OSCURO
# ============================================================

def build_light_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme_seed=PRIMARY_COLOR,
        use_material3=True,
    )

def build_dark_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme_seed=PRIMARY_DARK,
        use_material3=True,
    )


# ============================================================
#   BOTÓN DE DARK MODE (REUTILIZABLE)
# ============================================================

def build_darkmode_button(page: ft.Page) -> ft.IconButton:
    def toggle_theme(_):
        if page.theme_mode == ft.ThemeMode.DARK:
            page.theme_mode = ft.ThemeMode.LIGHT
            page.theme = build_light_theme()
        else:
            page.theme_mode = ft.ThemeMode.DARK
            page.theme = build_dark_theme()

        # 🔥 Actualizar gráfico circular si existe
        if hasattr(page, "fdt_app") and hasattr(page.fdt_app, "ventas_view"):
            ventas = page.fdt_app.ventas_view

            if hasattr(ventas, "grafico_circular") and ventas.grafico_circular:
                try:
                    ventas.grafico_circular.set_theme_mode(page.theme_mode)
                except Exception:
                    pass  # si el gráfico no está en pantalla, ignorar

        page.update()

    return ft.IconButton(
        icon=ft.Icons.DARK_MODE,
        tooltip="Cambiar modo oscuro/claro",
        on_click=toggle_theme,
    )




# ============================================================
#   ESTILOS COMUNES PARA BOTONES, TARJETAS, ETC.
# ============================================================

def styled_button(text: str, icon=None, on_click=None):
    """
    Un botón bonito, moderno y consistente con el diseño.
    """
    return ft.ElevatedButton(
        text,
        icon=icon,
        on_click=on_click,
        style=ft.ButtonStyle(
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=12),
            elevation={"hovered": 8, "default": 3},
        ),
    )
def date_filter_chip(text: str, dark_mode=False):
    """
    Chip suave para mostrar la fecha elegida.
    """
    if dark_mode:
        bg = ft.Colors.with_opacity(0.12, ft.Colors.WHITE)
        fg = ft.Colors.GREY_200
    else:
        bg = ft.Colors.with_opacity(0.12, ft.Colors.BLACK)
        fg = ft.Colors.GREY_700

    return ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.CALENDAR_MONTH, size=14, color=fg),
                ft.Text(text, size=11, color=fg),
            ],
            spacing=4,
        ),
        padding=6,
        border_radius=10,
        bgcolor=bg,
    )

def clear_filter_button_style():
    return ft.ButtonStyle( bgcolor={"default": ft.Colors.TRANSPARENT, "hovered": ft.Colors.with_opacity(0.65, ft.Colors.RED_100)},
                           color={"default": ft.Colors.RED, "hovered": ft.Colors.RED_700,}) 

def card_container(content):
    """
    Contenedor tipo "tarjeta" elegante, con sombras y bordes redondos.
    """
    return ft.Container(
        content=content,
        padding=20,
        border_radius=16,
        bgcolor=ft.Colors.with_opacity(0.85, CARD_LIGHT),
        shadow=ft.BoxShadow(
            blur_radius=10,
            spread_radius=1,
            color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
        ),
    )
