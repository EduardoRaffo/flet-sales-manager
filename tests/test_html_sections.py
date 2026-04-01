"""
Tests para reports/html_sections.py — Secciones HTML del informe.
"""

import unittest
from reports.html_sections import (
    render_chart_container,
    render_metrics,
    render_table_rows,
    render_period_filters,
)


class TestRenderChartContainer(unittest.TestCase):
    """Tests para render_chart_container()."""

    def test_contains_title(self):
        html = render_chart_container("Distribución", "abc123base64")
        self.assertIn("<h3>Distribución</h3>", html)

    def test_contains_image(self):
        html = render_chart_container("Test", "abc123")
        self.assertIn("data:image/png;base64,abc123", html)

    def test_subtitle_present(self):
        html = render_chart_container("Test", "abc", subtitle="Período A")
        self.assertIn("Período A", html)

    def test_no_subtitle(self):
        html = render_chart_container("Test", "abc")
        self.assertNotIn("subtitle", html.lower().replace("subtitle_html", ""))


class TestRenderMetrics(unittest.TestCase):
    """Tests para render_metrics()."""

    def test_contains_values(self):
        html = render_metrics(5000.0, 10, 500.0, 3, unique_clients=5)
        self.assertIn("5.000,00", html)
        self.assertIn("10", html)
        self.assertIn("500,00", html)
        self.assertIn("5", html)

    def test_zero_values(self):
        html = render_metrics(0, 0, 0, 0, unique_clients=0)
        self.assertIn("0,00", html)


class TestRenderTableRows(unittest.TestCase):
    """Tests para render_table_rows()."""

    def test_renders_rows(self):
        rows = [("Servicio", 5000.0, 10, 500.0, 100.0, 1000.0)]
        html = render_table_rows(rows)
        self.assertIn("Servicio", html)
        self.assertIn("5,000.00", html)

    def test_empty_rows(self):
        html = render_table_rows([])
        self.assertEqual(html, "")

    def test_invalid_row_skipped(self):
        rows = [("Only", "one")]  # IndexError on access
        html = render_table_rows(rows)
        self.assertEqual(html, "")


class TestRenderPeriodFilters(unittest.TestCase):
    """Tests para render_period_filters()."""

    def test_full_range(self):
        html = render_period_filters({"start_date": "2024-01-01", "end_date": "2024-06-30"})
        self.assertIn("2024-01-01", html)
        self.assertIn("2024-06-30", html)

    def test_no_dates_shows_all(self):
        html = render_period_filters({})
        self.assertIn("Todos los registros", html)

    def test_client_filter_shown(self):
        html = render_period_filters({"client_name": "TechNova"})
        self.assertIn("TechNova", html)
        self.assertIn("Cliente:", html)


if __name__ == "__main__":
    unittest.main()
