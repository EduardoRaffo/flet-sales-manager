import flet as ft
from user_ui import FDTApp
from theme import build_light_theme, build_dark_theme


def main(page: ft.Page):
    page.title = "FDT CRM Desktop App"
    page.window_width = 1100
    page.window_height = 750
    page.update()

    app = FDTApp(page)
    page.add(app)


ft.app(target=main)
