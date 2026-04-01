import pytest
from datetime import date
from unittest.mock import patch
from controllers.compare_controller import CompareController
from domain.compare_preset import PRESET_REGISTRY

def test_current_vs_previous_requires_a():
    c = CompareController()
    preset = PRESET_REGISTRY.get("current_vs_previous")
    assert c.apply_preset(preset) is False

def test_current_month_vs_previous_sets_b():
    c = CompareController()
    preset = PRESET_REGISTRY.get("current_month_vs_previous")
    assert c.apply_preset(preset) is True
    assert c.b_start is not None
    assert c.b_end is not None

def test_quarter_vs_previous_year_inherits_client_product():
    c = CompareController()
    c.set_client_a("ACME")
    c.set_product_a("SOFT")
    preset = PRESET_REGISTRY.get("quarter_vs_previous_year")
    assert c.apply_preset(preset) is True
    assert c.client_b == "ACME"
    assert c.product_b == "SOFT"
    
def test_current_vs_previous_sets_b():
    c = CompareController()
    c.set_period_a("2026-01-10", "2026-01-20")

    preset = PRESET_REGISTRY.get("current_vs_previous")
    assert c.apply_preset(preset) is True

    assert c.b_start == "2025-12-30"
    assert c.b_end == "2026-01-09"

def test_current_month_vs_previous_sets_a_and_b():
    c = CompareController()

    preset = PRESET_REGISTRY.get("current_month_vs_previous")
    assert preset is not None

    with patch("core.date_range.date") as mock_date:
        mock_date.today.return_value = date(2026, 5, 15)
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        applied = c.apply_preset(preset)

    assert applied is True

    # A = mes actual hasta hoy
    assert c.a_start == "2026-05-01"
    assert c.a_end == "2026-05-15"

    # B = mes anterior completo
    assert c.b_start == "2026-04-01"
    assert c.b_end == "2026-04-30"

def test_quarter_vs_previous_year_uses_date_range_only():
    c = CompareController()

    preset = PRESET_REGISTRY.get("quarter_vs_previous_year")
    assert preset is not None

    with patch("core.date_range.date") as mock_date:
        mock_date.today.return_value = date(2026, 5, 10)
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        applied = c.apply_preset(preset)

    assert applied is True

    # A = Q2 2026 hasta hoy
    assert c.a_start == "2026-04-01"
    assert c.a_end == "2026-05-10"

    # B = Q2 2025 completo
    assert c.b_start == "2025-04-01"
    assert c.b_end == "2025-06-30"

def test_current_semester_vs_previous():
    c = CompareController()

    preset = PRESET_REGISTRY.get("current_semester_vs_previous")
    assert preset is not None

    with patch("core.date_range.date") as mock_date:
        mock_date.today.return_value = date(2026, 3, 20)
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        applied = c.apply_preset(preset)

    assert applied is True

    # A = primer semestre hasta hoy
    assert c.a_start == "2026-01-01"
    assert c.a_end == "2026-03-20"

    # B = segundo semestre 2025
    assert c.b_start == "2025-07-01"
    assert c.b_end == "2025-12-31"

def test_presets_inherit_client_and_product():
    c = CompareController()
    c.set_client_a("ACME")
    c.set_product_a("SOFT")

    preset = PRESET_REGISTRY.get("current_month_vs_previous")
    assert preset is not None

    applied = c.apply_preset(preset)
    assert applied is True

    assert c.client_b == "ACME"
    assert c.product_b == "SOFT"
    assert c.client_b_overridden is False
    assert c.product_b_overridden is False


def test_presets_expose_expected_grouping_hints():
    expected = {
        "same_period_as_a": None,
        "period_vs_previous_year": None,
        "current_vs_previous": "day",
        "current_month_vs_previous": "week",
        "quarter_vs_previous_year": "month",
        "current_year_vs_previous": "month",
        "current_semester_vs_previous": "month",
    }

    for preset_id, expected_hint in expected.items():
        preset = PRESET_REGISTRY.get(preset_id)
        assert preset is not None
        assert preset.grouping_hint == expected_hint


def test_current_year_vs_previous():
    c = CompareController()

    preset = PRESET_REGISTRY.get("current_year_vs_previous")
    assert preset is not None

    with patch("core.date_range.date") as mock_date:
        mock_date.today.return_value = date(2026, 8, 3)
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        applied = c.apply_preset(preset)

    assert applied is True

    assert c.a_start == "2026-01-01"
    assert c.a_end == "2026-08-03"

    assert c.b_start == "2025-01-01"
    assert c.b_end == "2025-12-31"

def test_quarter_vs_previous_year_sets_dates():
    c = CompareController()

    preset = PRESET_REGISTRY.get("quarter_vs_previous_year")
    assert c.apply_preset(preset) is True

    assert c.a_start is not None
    assert c.b_start is not None
    assert c.b_end is not None
