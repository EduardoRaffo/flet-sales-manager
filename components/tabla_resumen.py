import flet as ft


class TablaResumen(ft.DataTable):
    def __init__(self, rows):
        super().__init__(
            columns=[
                ft.DataColumn(ft.Text("Producto", weight="bold")),
                ft.DataColumn(ft.Text("Total (€)", weight="bold")),
            ],
            rows=[
                ft.DataRow(
                    [
                        ft.DataCell(ft.Text(str(product))),
                        ft.DataCell(ft.Text(f"{total:.2f}")),
                    ]
                )
                for product, total in rows
            ],
        )
