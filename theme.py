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


def build_light_theme():
    return ft.Theme(
        color_scheme_seed=PRIMARY_COLOR,
        scaffold_bgcolor=BACKGROUND_LIGHT,
        visual_density=ft.ThemeVisualDensity.COMFORTABLE,
        use_material3=True,
    )


def build_dark_theme():
    return ft.Theme(
        color_scheme_seed=PRIMARY_DARK,
        scaffold_bgcolor=BACKGROUND_DARK,
        visual_density=ft.ThemeVisualDensity.COMFORTABLE,
        use_material3=True,
    )


# ============================================================
#   BOTÓN DE DARK MODE (REUTILIZABLE)
# ============================================================


def create_theme_toggle_button(page: ft.Page):
    """
    Devuelve un botón IconButton que cambia el tema global entre claro/oscuro.
    """

    def toggle_mode(e):
        page.theme_mode = (
            ft.ThemeMode.DARK
            if page.theme_mode == ft.ThemeMode.LIGHT
            else ft.ThemeMode.LIGHT
        )
        page.update()

    return ft.IconButton(
        icon=ft.Icons.DARK_MODE,
        tooltip="Cambiar modo claro/oscuro",
        icon_size=26,
        on_click=toggle_mode,
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
