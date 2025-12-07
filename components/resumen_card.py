import flet as ft


class ResumenCard(ft.Container):
    def __init__(self, promedio):
        super().__init__(
            content=ft.Text(
                f"✨ Ticket medio: {promedio:.2f} €",
                size=18,
                weight="bold",
                color=ft.Colors.BLACK,
            ),
            bgcolor=ft.Colors.GREEN_200,
            padding=15,
            border_radius=12,
        )
