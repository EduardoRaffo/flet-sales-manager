"""Punto de entrada de Sales CRM Desktop.

Inicializa la base de datos, configura la página Flet (tema, icono, dimensiones)
y lanza la aplicación principal. Ejecutar con: python main.py
"""

import flet as ft
from ui.user_ui import FDTApp
from theme import build_light_theme, build_dark_theme
from core.db import init_db, get_base_path
import traceback
import sys

def main(page: ft.Page):
    try:
        # Ocultar ventana durante inicialización
        page.window.visible = False
        # Inicializar BD
        init_db()
        
        # Configurar página
        page.title = "Sales CRM Desktop"
        page.window.height = 720
        
       # Ruta a assets (compatible con .exe compilado)
        base_path = get_base_path()
        icon_path = base_path / "assets" / "fdt_logo.ico"
        
        if icon_path.exists():
            page.window.icon = str(icon_path)
        
        # Configurar temas (patrón oficial de Flet)
        page.theme = build_light_theme()
        page.dark_theme = build_dark_theme()
        page.theme_mode = ft.ThemeMode.LIGHT
        page.bgcolor = None  
        
        # Crear app
        app = FDTApp(page)        
        page.add(app)
        page.window.visible = True
    except Exception as e:
         print("Error fatal al iniciar la aplicación:")
         print(f"   {str(e)}")
         traceback.print_exc()
         sys.exit(1)

if __name__ == "__main__":
    try:
        ft.run(main)
    except (ConnectionResetError, BrokenPipeError, OSError):
        # Errores de cleanup asyncio en Windows al cerrar — ignorar
        pass