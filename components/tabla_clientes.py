import flet as ft


class TablaClientes(ft.DataTable):
    def __init__(self, clients, view):
        super().__init__(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("CIF")),
                ft.DataColumn(ft.Text("Email")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[
                ft.DataRow(
                    [
                        ft.DataCell(ft.Text(str(id))),
                        ft.DataCell(ft.Text(name)),
                        ft.DataCell(ft.Text(cif)),
                        ft.DataCell(ft.Text(email)),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        ft.Icons.EDIT,
                                        on_click=lambda e, cid=id: view.show_edit_form(
                                            cid
                                        ),
                                    ),
                                    ft.IconButton(
                                        ft.Icons.DELETE,
                                        on_click=lambda e, cid=id: view.delete_client(
                                            cid
                                        ),
                                    ),
                                ]
                            )
                        ),
                    ]
                )
                for (id, name, cif, address, contact, email) in clients
            ],
        )
