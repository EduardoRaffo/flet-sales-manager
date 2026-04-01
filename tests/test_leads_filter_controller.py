"""
Tests para controllers/leads_filter_controller.py — Filtrado puro de leads.
"""

import unittest
from unittest.mock import patch
from datetime import date, timedelta
from controllers.leads_filter_controller import filter_leads, _STAGE_STATUS_MAP, _DATE_RANGE_OPTIONS


# ── Datos de prueba ───────────────────────────────────────────

SAMPLE_LEADS = [
    {"id": "L001", "source": "meta_ads", "status": "new", "created_at": "2024-05-01", "client_name": "TechNova"},
    {"id": "L002", "source": "google_ads", "status": "contacted", "created_at": "2024-05-03", "client_name": "DataCorp"},
    {"id": "L003", "source": "meta_ads", "status": "meeting", "created_at": "2024-05-05", "client_name": "CloudSoft"},
    {"id": "L004", "source": "linkedin_ads", "status": "converted", "created_at": "2024-04-20", "client_name": "TechNova"},
    {"id": "L005", "source": "google_ads", "status": "lost", "created_at": "2024-05-08", "client_name": ""},
]


class TestFilterLeadsNoFilters(unittest.TestCase):
    """Sin filtros activos devuelve todos los leads."""

    def test_no_filters_returns_all(self):
        result = filter_leads(SAMPLE_LEADS)
        self.assertEqual(len(result), 5)

    def test_empty_leads_returns_empty(self):
        result = filter_leads([])
        self.assertEqual(result, [])


class TestFilterLeadsBySource(unittest.TestCase):
    """Filtrado por fuente."""

    def test_filter_by_source(self):
        result = filter_leads(SAMPLE_LEADS, source="meta_ads")
        self.assertEqual(len(result), 2)
        self.assertTrue(all(ld["source"] == "meta_ads" for ld in result))

    def test_source_todas_ignored(self):
        result = filter_leads(SAMPLE_LEADS, source="Todas")
        self.assertEqual(len(result), 5)

    def test_source_none_ignored(self):
        result = filter_leads(SAMPLE_LEADS, source=None)
        self.assertEqual(len(result), 5)


class TestFilterLeadsByStage(unittest.TestCase):
    """Filtrado por etapa del funnel."""

    def test_filter_by_stage_lead(self):
        result = filter_leads(SAMPLE_LEADS, stage="Lead")
        self.assertTrue(all(ld["status"] == "new" for ld in result))

    def test_filter_by_stage_contactado(self):
        result = filter_leads(SAMPLE_LEADS, stage="Contactado")
        self.assertTrue(all(ld["status"] == "contacted" for ld in result))

    def test_stage_todos_ignored(self):
        result = filter_leads(SAMPLE_LEADS, stage="Todos")
        self.assertEqual(len(result), 5)

    def test_stage_status_map_complete(self):
        expected_stages = {"Lead", "Contactado", "Reunión", "Cliente", "Perdido"}
        self.assertEqual(set(_STAGE_STATUS_MAP.keys()), expected_stages)


class TestFilterLeadsByDate(unittest.TestCase):
    """Filtrado por fechas."""

    def test_filter_by_explicit_dates(self):
        result = filter_leads(SAMPLE_LEADS, start_date="2024-05-01", end_date="2024-05-05")
        self.assertEqual(len(result), 3)

    def test_explicit_dates_priority_over_label(self):
        """Fechas explícitas tienen prioridad sobre date_label."""
        result = filter_leads(
            SAMPLE_LEADS,
            date_label="7 días",
            start_date="2024-05-01",
            end_date="2024-05-03",
        )
        self.assertEqual(len(result), 2)

    @patch("controllers.leads_filter_controller.date")
    def test_filter_by_date_label_7_dias(self, mock_date):
        mock_date.today.return_value = date(2024, 5, 10)
        mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
        result = filter_leads(SAMPLE_LEADS, date_label="7 días")
        for ld in result:
            self.assertGreaterEqual(ld["created_at"][:10], "2024-05-03")

    def test_date_label_todo_no_filter(self):
        result = filter_leads(SAMPLE_LEADS, date_label="Todo")
        self.assertEqual(len(result), 5)


class TestFilterLeadsBySearch(unittest.TestCase):
    """Filtrado por término de búsqueda."""

    def test_search_term_case_insensitive(self):
        result = filter_leads(SAMPLE_LEADS, search_term="technova")
        self.assertTrue(len(result) >= 1)
        self.assertTrue(any(ld["client_name"] == "TechNova" for ld in result))

    def test_search_by_id(self):
        result = filter_leads(SAMPLE_LEADS, search_term="L003")
        self.assertEqual(len(result), 1)

    def test_search_no_match(self):
        result = filter_leads(SAMPLE_LEADS, search_term="zzzznonexistent")
        self.assertEqual(len(result), 0)


class TestFilterLeadsCombined(unittest.TestCase):
    """Filtros combinados (AND logic)."""

    def test_source_and_stage(self):
        result = filter_leads(SAMPLE_LEADS, source="meta_ads", stage="Lead")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "L001")

    def test_all_filters_combined(self):
        result = filter_leads(
            SAMPLE_LEADS,
            source="meta_ads",
            stage="Lead",
            start_date="2024-05-01",
            end_date="2024-05-10",
            search_term="tech",
        )
        self.assertEqual(len(result), 1)


if __name__ == "__main__":
    unittest.main()
