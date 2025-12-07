import flet as ft


class TablaResumen(ft.DataTable):
    def __init__(self, rows, columns=None):
        """
        rows: lista de tuplas con los datos
        columns: lista de nombres de columnas (opcional)
        """
        if not rows:
            rows = []

        # Si no hay columnas especificadas, asumir primeras 2
        if columns is None:
            columns = ["Producto", "Total (€)"]

        data_rows = []

        for row in rows:
            formatted_cells = []

            # Procesar cada valor
            for idx, value in enumerate(row[:len(columns)]):

                # ----------------------------
                # ¿Es número? → formateo + alineación derecha + tooltip
                # ----------------------------
                if isinstance(value, (int, float)):

                    # Guardamos el valor original para el tooltip
                    valor_original = str(value)

                    # Formato profesional español con miles y coma decimal
                    formatted_value = (
                        f"{value:,.2f}"
                        .replace(",", "X")
                        .replace(".", ",")
                        .replace("X", ".")
                    )

                    cell = ft.DataCell(
                        ft.Text(
                            formatted_value,
                            text_align=ft.TextAlign.RIGHT,   # 🔥 Alineación derecha
                            tooltip=valor_original           # 🔥 Tooltip con valor real
                        )
                    )

                else:
                    # Texto normal (producto, categoría, etc.)
                    cell = ft.DataCell(
                        ft.Text(
                            str(value),
                            text_align=ft.TextAlign.LEFT,
                        )
                    )

                formatted_cells.append(cell)

            data_rows.append(ft.DataRow(formatted_cells))

        # Crear columnas dinámicamente
        data_columns = [
            ft.DataColumn(
                ft.Text(col, weight="bold"),
                numeric=(i > 0)  # Hace que la cabecera también se alinee a la derecha en columnas numéricas
            )
            for i, col in enumerate(columns)
        ]

        super().__init__(
            columns=data_columns,
            rows=data_rows,
        )
