import flet as ft
from client_manager import (
    add_client,
    get_clients,
    get_client_by_id,
    update_client,
    delete_client,
)
from validations_client import (
    validate_name,
    validate_cif,
    validate_email,
    validate_contact,
)
from components.tabla_clientes import TablaClientes


class ClientesView(ft.Column):
    def __init__(self, page):
        super().__init__(expand=True, spacing=20)
        self.page = page

        self.output = ft.Text(size=14)
        self.list_container = ft.Container()

        self.controls = [
            ft.Text("👥 Gestión de Clientes", size=24, weight="bold"),
            ft.ElevatedButton(
                "Añadir Cliente",
                icon=ft.Icons.PERSON_ADD,
                on_click=lambda _: self.show_add_form(),
            ),
            self.list_container,
            self.output,
        ]

        self.refresh()

    def refresh(self):
        clients = get_clients()
        self.list_container.content = TablaClientes(clients, self)
        self.page.update()

    # ---------------------------
    # Formulario añadir cliente
    # ---------------------------
    def show_add_form(self):
        name = ft.TextField(label="Nombre")
        cif = ft.TextField(label="CIF")
        address = ft.TextField(label="Dirección")
        contact = ft.TextField(label="Contacto")
        email = ft.TextField(label="Email")

        def save(e):
            if not validate_name(name.value):
                self.output.value = "❌ Nombre inválido."
            elif not validate_cif(cif.value):
                self.output.value = "❌ CIF inválido."
            elif not validate_email(email.value):
                self.output.value = "❌ Email inválido."
            elif not validate_contact(contact.value):
                self.output.value = "❌ Contacto inválido."
            else:
                add_client(
                    name.value, cif.value, address.value, contact.value, email.value
                )
                self.output.value = "✔ Cliente añadido."
                self.refresh()
                return

            self.page.update()

        self.list_container.content = ft.Column(
            [
                ft.Text("➕ Añadir Cliente", size=22, weight="bold"),
                name,
                cif,
                address,
                contact,
                email,
                ft.Row(
                    [
                        ft.ElevatedButton("Guardar", on_click=save, icon=ft.Icons.SAVE),
                        ft.TextButton("Cancelar", on_click=lambda _: self.refresh()),
                    ]
                ),
            ]
        )

        self.page.update()

    # ---------------------------
    # Formulario editar cliente
    # ---------------------------
    def show_edit_form(self, id):
        client = get_client_by_id(id)
        if not client:
            self.output.value = "❌ Cliente no encontrado."
            self.page.update()
            return

        _, name_val, cif_val, address_val, contact_val, email_val = client

        name = ft.TextField(label="Nombre", value=name_val)
        cif = ft.TextField(label="CIF", value=cif_val)
        address = ft.TextField(label="Dirección", value=address_val)
        contact = ft.TextField(label="Contacto", value=contact_val)
        email = ft.TextField(label="Email", value=email_val)

        def save(e):
            if not validate_name(name.value):
                self.output.value = "❌ Nombre inválido."
            elif not validate_cif(cif.value):
                self.output.value = "❌ CIF inválido."
            elif not validate_email(email.value):
                self.output.value = "❌ Email inválido."
            elif not validate_contact(contact.value):
                self.output.value = "❌ Contacto inválido."
            else:
                update_client(
                    id, name.value, cif.value, address.value, contact.value, email.value
                )
                self.output.value = "✔ Cliente actualizado."
                self.refresh()
                return

            self.page.update()

        self.list_container.content = ft.Column(
            [
                ft.Text("✏ Editar Cliente", size=22, weight="bold"),
                name,
                cif,
                address,
                contact,
                email,
                ft.Row(
                    [
                        ft.ElevatedButton("Guardar", on_click=save, icon=ft.Icons.SAVE),
                        ft.TextButton("Cancelar", on_click=lambda _: self.refresh()),
                    ]
                ),
            ]
        )

        self.page.update()

    def delete_client(self, id):
        delete_client(id)
        self.output.value = "✔ Cliente eliminado."
        self.refresh()
