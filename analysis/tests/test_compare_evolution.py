def test_compare_evolution_basic_structure(monkeypatch):
    from analysis.evolution_analysis import get_compare_evolution_rows

    def fake_group(rows, grouping):
        return [
            {"key": "2024-01", "label": "Jan 24", "total": 100.0}
        ]

    monkeypatch.setattr(
        "analysis.evolution_analysis.group_time_series",
        fake_group
    )

    result = get_compare_evolution_rows(
        "2024-01-01", "2024-01-31",
        "2023-01-01", "2023-01-31",
        grouping="month",
    )

    assert "rows" in result
    assert "meta" in result
    assert result["meta"]["grouping"] == "month"

def test_compare_evolution_aligns_disjoint_ranges(monkeypatch):
    from analysis.evolution_analysis import get_compare_evolution_rows

    class FakeCursor:
        def __init__(self, rows):
            self._rows = rows
            self.description = [("date",), ("total",)]

        def fetchall(self):
            return self._rows

    class FakeConnection:
        def execute(self, query, params):
            if params and params[0] == "2024-01-01":
                # Dataset A: Jan–Feb 2024
                return FakeCursor([
                    ("2024-01-01", 100.0),
                    ("2024-02-01", 200.0),
                ])
            # Dataset B: Feb–Mar 2024
            return FakeCursor([
                ("2024-02-01", 50.0),
                ("2024-03-01", 75.0),
            ])

        def close(self):
            pass

    def fake_get_db_connection():
        return FakeConnection()

    monkeypatch.setattr(
        "analysis.evolution_analysis.get_db_connection",
        fake_get_db_connection
    )

    result = get_compare_evolution_rows(
        "2024-01-01", "2024-02-28",
        "2024-02-01", "2024-03-31",
        grouping="month",
    )

    assert result["rows"] == [
        {"label": "Jan 24", "A": 100.0, "B": 0.0},
        {"label": "Feb 24", "A": 200.0, "B": 50.0},
        {"label": "Mar 24", "A": 0.0, "B": 75.0},
    ]
