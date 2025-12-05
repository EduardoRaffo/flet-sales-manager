import flet as ft
from user_ui import FDTApp
from theme import build_light_theme, build_dark_theme
from db import init_db  # ← AÑADIR


def main(page: ft.Page):
    init_db()  # ← INICIALIZA LA BASE DE DATOS
    
    page.title = "FDT CRM Desktop App"
    page.window_width = 1280
    page.window_height = 720
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = build_light_theme()
    page.update()

    app = FDTApp(page)
    page.fdt_app = app
    page.add(app)


ft.app(target=main)
